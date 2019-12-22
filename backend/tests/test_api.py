import json
import unittest
import os
from unittest.mock import patch
from functools import wraps
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from api.database.models import setup_db, Drink, db_drop_and_create_all
from api import create_app
import sys
from pathlib import Path
sys.path.append(Path(__file__).resolve().parent.parent)


def mock_decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


@patch('api.auth.auth.requires_auth_wrapper')
class CoffeeShopTestCase(unittest.TestCase):
    '''
    Test Coffee Shop APIs
    '''

    def setUp(self):
        """
        Define test variables and initialize app.
        """
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client
        setup_db(self.app)

    def tearDown(self):
        """Executed after reach test"""
        db_drop_and_create_all()
        pass

    def test_create_drinks(self, mock_requires_auth_wrapper):
        res = self.client().post('/drinks', json={
            'title': 'Test coffee',
            'recipe': [{"name": "tea", "color": "green", "parts": 5}]
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_create_drinks_fail(self, mock_requires_auth_wrapper):
        res = self.client().post('/drinks', json={
            'title': 'Fail coffee',
        })
        data = json.loads(res.data)
        self.assertNotEqual(res.status_code, 200)

    def test_get_drinks(self, mock_requires_auth_wrapper):
        res = self.client().get('/drinks')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['drinks']), 0)

    def test_get_drinks_detail(self, mock_requires_auth_wrapper):
        res = self.client().get('/drinks-detail')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['drinks']), 0)

    def test_resource_not_found(self, mock_requires_auth_wrapper):
        res = self.client().get('/empty')
        self.assertEqual(res.status_code, 404)

    def test_patch_drink(self, mock_requires_auth_wrapper):
        res = self.client().post('/drinks', json={
            'title': 'Test coffee2',
            'recipe': [{"name": "tea", "color": "green", "parts": 5}]
        })
        data = json.loads(res.data)
        drink_id = data['drinks'][0]['id']
        res = self.client().patch('/drinks/{}'.format(drink_id), json={
            'title': 'Test coffees',
            'recipe': [{"name": "tea", "color": "green", "parts": 8}]
        })
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(res.status_code, 200)

    def test_patch_drink_fail(self, mock_requires_auth_wrapper):
        res = self.client().patch('/drinks/300', json={
            'title': 'Test coffee',
            'recipe': [{"name": "tea", "color": "green", "parts": 8}]
        })
        data = json.loads(res.data)
        self.assertNotEqual(res.status_code, 200)
        self.assertFalse(data['success'])

    def test_delete_drink(self, mock_requires_auth_wrapper):
        res = self.client().post('/drinks', json={
            'title': 'Test coffee2',
            'recipe': [{"name": "tea", "color": "green", "parts": 5}]
        })
        data = json.loads(res.data)
        drink_id = data['drinks'][0]['id']
        res = self.client().delete('/drinks/{}'.format(drink_id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_delete_drink_fail(self, mock_requires_auth_wrapper):
        res = self.client().delete('/drinks/500')
        data = json.loads(res.data)
        self.assertNotEqual(res.status_code, 200)
        self.assertFalse(data['success'])
