import boto3
from utils import *
import time
import json
import requests
from datetime import datetime
from datetime import timedelta
import humanize

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

def auth(event, context):
	set_debug(event)
	user_id = event['user_id']
	user_id = parse_user(user_id)

	friend_ids = event['friend_ids']
	friend_ids = [parse_user(i) for i in friend_ids]

	friend_names = event['friend_names']
	refresh_token = event['refresh_token']
	
	utable = table_init('users')
	user_init(utable, user_id)

	data = {
		f[0]:f[1]
	for f in list(zip(friend_ids, friend_names))}
	data['refresh_token'] = refresh_token
	user_social_add(utable, user_id, 'friends_card', data)

	
def get_info(event, context):
	set_debug(event)
	user_id = event['user_id']
	user_id = parse_user(user_id)

	utable = table_init('users')

	user = utable.get_item(Key={"user_id":str(user_id)})
	assert "Item" in user

	ret = {}
	for friend_id in user['Item']['social']['friends_card']:
		if friend_id == 'refresh_token':
			continue
		friend_name = user['Item']['social']['friends_card'][friend_id]
		friend_data = utable.get_item(Key = {'user_id':str(friend_id)})
		if 'Item' not in friend_data:
			ret[friend_id]={
				'name':friend_name,
				'busy':False,
				'status':"",
				'event_title':"",
				'on_iris':False,
			}
			continue
		if not 'friends_card' in friend_data['Item']['social']:
			ret[friend_id]={
				'name':friend_name,
				'busy':False,
				'status':"",
				'event_title':"",
				'on_iris':False,
			}
			continue
		friend_refresh = friend_data['Item']['social']['friends_card']['refresh_token']
		token = refresh('creds.json', friend_refresh)
		# print(token)
		params = {
			'orderBy':'startTime',
			'singleEvents':True,
			'maxResults':1,
			'timeMin':(datetime.now()-timedelta(hours=7)).strftime('%Y-%m-%dT%H:%M:%S')+'-07:00',
			# 'timeMax':(datetime.today()+timedelta(days=1)).strftime('%Y-%m-%d')+'T00:00:00Z',
			# 'timeZone':'PST'
		}
		req_string = f'https://www.googleapis.com/calendar/v3/calendars/primary/events'#?access_token={token}'
		r = requests.get(req_string, params=params, headers={'Authorization': f"Bearer {token}"})
		if r.ok:
			data = r.json()
			print(data)
		else:
			print(r)
			continue

		event = data["items"][0]
		title = event['summary']
		start = event['start']['dateTime']
		end = event['end']['dateTime']

		rfc3339 = '%Y-%m-%dT%H:%M:%S-07:00'
		start_dt = datetime.strptime(start, rfc3339)#-timedelta(hours=7)
		end_dt = datetime.strptime(end, rfc3339)#-timedelta(hours=7)
		now_dt = datetime.now()-timedelta(hours=7)
		if start_dt<now_dt<end_dt:
			busy = True
			status = f"In event for {humanize.naturaldelta(end_dt-now_dt)}"
			event_title = title
		else:
			busy = False
			status = f"No events for {humanize.naturaldelta(start_dt-now_dt)}"
			event_title = ""
		ret[friend_id] = {
			#'times':f"Start: {str(start_dt)}, End: {str(end_dt)}, Now: {str(now_dt)}",
			'name':friend_name,
			'busy':busy,
			'event_title':event_title,
			'status':status,
			'on_iris':True
		}
				
	ret = json.loads(json.dumps(ret))
	print(ret)
	return ret