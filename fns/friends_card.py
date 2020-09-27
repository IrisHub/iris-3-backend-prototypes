import boto3
from utils import *
import time
import json
import requests

def refresh(client_json, refresh_token):
	with open(client_json, 'r') as f:
		data = json.load(f)
		client_id = data['web']['client_id']
		client_secret = data['web']['client_secret']
	params = {
		'grant_type':'refresh_token',
		'client_id':client_id,
		'client_secret':client_secret,
		'refresh_token':refresh_token
	}
	url="https://www.googleapis.com/oauth2/v4/token"
	r = requests.post(url, params=params)
	# print(r)
	if r.ok:
		return r.json()['access_token']
	else:
		return None