import boto3
import requests
import json
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

def event_handler(event, context):
	print(event)
	user_id = event['user_id']

	user_id = "".join(filter(str.isdigit, user_id))[-10:]
	user_id = user_id[:]

	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('contacts_experiments')

	user = table.get_item(Key={"user_id":str(user_id)})
	print(user)
	ret = {}
	if "Item" in user:
		for friend in user['Item']['friends'].keys():
			print(f"Friend: {friend}")
			friend_name = user['Item']['friends'][friend]['name']
			refresh_token = user['Item']['friends'][friend]['refresh_token']
			if not refresh_token:
				ret[friend]={
					'name':friend_name,
					'busy':False,
					'status':"",
					'event_title':"",
					'on_iris':False,
				}
				continue
			token = refresh('creds.json', refresh_token)
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
			ret[friend] = {
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

# def __main__():
# 	event_handler({'user_id':"2"}, None)

# __main__()

