from os.path import exists
from os import environ
from string import Template

import plaid
from plaid.api import plaid_api
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

from flask import Flask
from flask import request
from flask import send_file
from dotenv import load_dotenv

load_dotenv()

PORT=environ['PORT_NUMBER']

def env_lookup():
    env = environ['PLAID_ENV']
    if env == 'sandbox':
        return plaid.Environment.Sandbox
    if env == 'development':
        return plaid.Environment.Development
    if env == 'production':
        return plaid.Environment.Production
    raise Exception('Expected one of [sandbox|development|production] as an environment.')

def init_client():
    configuration = plaid.Configuration(
        host=env_lookup(),
        api_key={
            'clientId': environ['PLAID_CLIENT_ID'],
            'secret': environ['PLAID_SECRET']
        }
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


client = init_client()
app = Flask(environ['APPLICATION_NAME'])


@app.route("/api/exchange-public-token", methods=['POST'])
def exchange_public_token():    
    exchange_request = ItemPublicTokenExchangeRequest(public_token=request.json['public_token'])
    exchange_response = client.item_public_token_exchange(exchange_request)
    access_token = exchange_response['access_token']
    with open(environ['ACCESS_TOKEN_STORAGE'], 'w') as f:
        f.write(access_token)
    return f"Access token written to: {environ['ACCESS_TOKEN_STORAGE']}"


@app.route("/api/create-link-token", methods=['GET'])
def create_link_token():
    req = LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name=environ['APPLICATION_NAME'],
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id='absent-user'
            ),
            redirect_uri=environ['PLAID_SANDBOX_REDIRECT_URI']
        )
    response = client.link_token_create(req)
    return response.to_dict()


@app.route("/", methods=['GET'])
def create_link():    
    template = 'home.html'
    if exists(environ['ACCESS_TOKEN_STORAGE']):
        template = 'exists.html'
        
    with open(template, "r") as file:
        data = file.read()

    t = Template(data)
    return t.safe_substitute(access_token_storage=environ['ACCESS_TOKEN_STORAGE'])


@app.route('/icon.svg')
def icon():
    return send_file('icon.svg', mimetype='image/svg+xml')


if __name__ == "__main__":
    app.run(port=PORT)
