import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    # NOTE: uncomment this for initial run
    # db_drop_and_create_all()

    # ROUTES
    '''
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks')
    def get_drinks():
        try:
            drinks = Drink.query.all()
            return jsonify({
                "success": True,
                "drinks": [drink.short() for drink in drinks]
            })
        except Exception:
            print(sys.exc_info())
            abort(500)

    '''
    GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
            where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks-detail')
    @requires_auth('get:drinks-detail')
    def get_drinks_detail(jwt):
        try:
            drinks = Drink.query.all()
            return jsonify({
                "success": True,
                "drinks": [drink.long() for drink in drinks]
            })
        except Exception:
            print(sys.exc_info())
            abort(500)

    '''
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks', methods=['POST'])
    @requires_auth('post:drinks')
    def create_drink(jwt):
        try:
            data = request.get_json()
            title = data.get('title')
            recipe = data.get('recipe')
            if title and recipe is not None:
                recipe_str = json.dumps(recipe)
                drink = Drink(title=title,
                              recipe=recipe_str)
                drink.insert()
                return jsonify({
                    'success': True,
                    'drinks': [drink.long()]
                })
            else:
                raise ValueError
        except ValueError:
            abort(422)
        except Exception:
            abort(500)
    '''
    PATCH /drinks/<id>
    where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks/<int:drink_id>', methods=['PATCH'])
    @requires_auth('patch:drinks')
    def update_drink(jwt, drink_id):
        try:
            drink = Drink.query.filter_by(id=drink_id).one_or_none()
            if drink is None:
                abort(404)

            data = request.get_json()
            title = data.get('title')
            recipe = data.get('recipe')
            if title and recipe is not None:
                drink.recipe = json.dumps(recipe)
                drink.title = title
                drink.update()
                return jsonify({
                    'success': True,
                    'drinks': [drink.long()]
                })
            else:
                raise ValueError
        except ValueError:
            abort(422)
        except Exception:
            print(sys.exc_info())
            abort(500)

    '''
    DELETE /drinks/<id>
    where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
        where id is the id of the deleted record
        or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks/<int:drink_id>', methods=['DELETE'])
    @requires_auth('delete:drinks')
    def delete_drink(jwt, drink_id):
        try:
            drink = Drink.query.filter_by(id=drink_id).one_or_none()
            if drink is None:
                abort(404)
            drink.delete()
            return jsonify({
                'success': True,
                'delete': drink.id
            })
        except Exception:
            abort(500)

    # Error Handling
    @app.errorhandler(422)
    def unprocessable_entity(e):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(404)
    def unprocessable_entity(e):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(500)
    def unprocessable_entity(e):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({
            "success": False,
            "error": 403,
            "message": "permission error"
        }), 403

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({
            "success": False,
            "error": 401,
            "message": "unauthorized"
        }), 401

    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response
    return app
