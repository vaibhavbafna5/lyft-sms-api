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

class RideRequest:
    state = 'justTalking'
    start_lat = 0.0
    start_lon = 0.0
    end_lat = 0.0
    end_lon = 0.0
    ride_type = "lyft"

ride_request = RideRequest()

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
    # get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    # Start our TwiML response
    resp = MessagingResponse()
    msg = ""

    print("HERE: AT EVERY REQUEST: ", ride_request.state)

    # Determine the right reply for this message

    if 'Pickup location' in body: 
        split_address = body.split('Pickup location:', 1)
        address = split_address[1]

        # get lat long here 
        pickup_lat_lon = get_lat_lon(address)
        ride_request.start_lat = pickup_lat_lon[0]
        ride_request.start_lon = pickup_lat_lon[1]

        msg = "Your pickup address is: " + address + ". Text \"Dropoff location: <address>\" to continue."
        ride_request.state = 'pickupLocationEntered'
        resp.message(msg)

    elif 'Dropoff location:' in body: 
        split_address = body.split('Dropoff location:', 1)
        address = split_address[1]
        print("AYYOO LOOK HERE: ", address)

        #get lat long here 
        dropoff_lat_lon = get_lat_lon(address)
        ride_request.end_lat = dropoff_lat_lon[0]
        ride_request.end_lon = dropoff_lat_lon[1]

        # response = client.request_ride(
        #     ride_type="lyft",
        #     start_latitude=ride_request.start_lat,
        #     start_longitude=ride_request.start_lon,
        #     end_latitude=ride_request.end_lat,
        #     end_longitude=-ride_request.end_lon,
        # )

        msg = "Your dropoff address is: " + address + ". Requesting your Lyft now!"
        resp.message(msg)

        msg = "Your Lyft is on its way. Look out for Tyler in a Blue Prius (BMX798)!"
        resp.message(msg)

    elif 'Pickup location' not in body: 
        msg = "Hey, welcome to Lyft! To start ordering a Lyft, text \"Pickup location: <address>\""
        resp.message(msg)
    
    return str(resp)

def get_lat_lon(address): 
    r = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address=" + address + "&key=AIzaSyAAUTtrJ63mSvQm7aFVbOIwQYkJhBBA35o")
    data = r.json()
    lat = data['results'][0]["geometry"]["location"]["lat"]
    lon = data['results'][0]["geometry"]["location"]["lng"]
    return (lat, lon)