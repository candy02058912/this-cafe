/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'https://agile-hamlet-83231.herokuapp.com', // the running FLASK api server url
  auth0: {
    url: 'riji', // the auth0 domain prefix
    audience: 'dev', // the audience set for the auth0 app
    clientId: '71DKzlfPKcAoVNsrcIyTyIj11z4flHnY', // the client id generated for the auth0 app
    callbackURL: 'https://this-cafe.netlify.com' // the base url of the running ionic application.
  }
};
