from flask import Flask, jsonify, abort, make_response, request
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

'''
possible states:
- justTalking
- pickupLocationEntered
- rideRequestPending
- rideRequestAccepted
- driverArrived
'''

state = 'justTalking'

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

@app.route("/bio", methods=['GET'])
def get_ridetypes(): 
    response = client.get_user_profile()
    print(response)
    return jsonify({'response': 'success'})

@app.route("/", methods=['GET'])
def say_hi():
    return jsonify({"response": "Hello."})

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    # Start our TwiML response
    resp = MessagingResponse()
    msg = ""

    # Determine the right reply for this message

    # gets pickup location 
    if state == 'justTalking' and 'Pickup location' not in body: 
        msg = "Hey, welcome to Lyft! To start ordering a Lyft, text 'Pickup location: <address>"
        
    if state == 'justTalking' and 'Pickup location' in body: 
        split_address = body.split('Pickup location:', 1)
        address = split_address[1]
        msg = "Your address is: " + address
        state == 'pickupLocationEntered'
    # if state == 'justTalking' and 'Pickup location:' in body:
    #     msg = ""
    #     state = 'pickupLocationEntered'
    #     break
    # elif state == 'pickupLocationEntered' and 'Dropoff location:' in body:
    #     msg = ""
    #     state = "rideRequestPending"
    #     # make request here
    #     break

    resp.message(msg)
    return str(resp)

def sms_ahoy_reply():
    """Hi cutie."""
    # Start our response
    resp = MessagingResponse()
    resp.message("Hi cutie")
    return str(resp)