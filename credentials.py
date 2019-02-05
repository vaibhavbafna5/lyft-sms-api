from lyft_rides.auth import ClientCredentialGrant
from lyft_rides.session import Session
from lyft_rides.auth import AuthorizationCodeGrant
from lyft_rides.client import LyftRidesClient

client_id = "PxRATSRJrP4l"
client_secret = "ksbAnrp0udSX-XwicMaDf8mdK6f4fRS3"

auth_flow = AuthorizationCodeGrant(
    client_id,
    client_secret,
    ['public', 'ride.request', 'ride.read'],
)
# auth_url = auth_flow.get_authorization_url()
# print(auth_url)


redirect_url = 'https://lyft-sms-api.herokuapp.com/?code=7UCSSiTHHH2bp7dW&state=BEhYvgRgDpMqREBNwLXcOTWPsknXZU6F'

session = auth_flow.get_session(redirect_url)
client = LyftRidesClient(session)
credentials = session.oauth2credential

response = client.get_ride_types(37.7833, -122.4167)
ride_types = response.json.get('ride_types')
print(ride_types)