from flask import Flask, jsonify, abort, make_response
from flask_cors import CORS
import requests
from lyft_rides.auth import ClientCredentialGrant
from lyft_rides.session import Session
from lyft_rides.session import OAuth2Credential
from lyft_rides.client import LyftRidesClient
from yaml import safe_load
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
cors = CORS(app)

oauth_filename = 'examples/oauth2_session_store.yaml'
with open(oauth_filename, 'r' ) as config_file:
    config = safe_load(config_file)

oauth2 = OAuth2Credential(
    client_id=config['client_id'],
    access_token=config['access_token'],
    expires_in_seconds=config['expires_in_seconds'],
    scopes=config['scopes'],
    grant_type=config['grant_type'],
    client_secret=config['client_secret'],
    refresh_token=config['refresh_token']
)
session = Session(oauth2)
client = LyftRidesClient(session)

@app.route("/ridetypes", methods=['GET'])
def get_ridetypes(): 
    response = client.get_ride_types(47.6, -122)
    ride_types = response.json.get('ride_types')
    print(ride_types[0])
    return jsonify({'ride_types': ride_types})

@app.route("/", methods=['GET'])
def say_hi():
    return jsonify({"response": "Hello."})

@app.route("/sms", methods=['GET', 'POST'])
def sms_ahoy_reply():
    """Respond to incoming messages with a friendly SMS."""
    # Start our response
    resp = MessagingResponse()
    resp.message("Responses are working")
    return str(resp)