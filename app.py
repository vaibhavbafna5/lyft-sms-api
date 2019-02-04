from flask import Flask, jsonify, abort, make_response
from flask_cors import CORS
import requests

app = Flask(__name__)
cors = CORS(app)

@app.route("/", methods=['GET'])
def say_hi():
    return jsonify({"response": "Hello."})