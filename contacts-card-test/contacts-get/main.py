import boto3
from datetime import datetime
from datetime import timedelta
import random
import json

def get_leaderboard(user_id, table, friends):
	board = []
	for friend in friends:
		friend_id = friend['id']
		user = table.get_item(Key={"user_id":str(friend_id)})
		if "Item" not in user:
			board.append({
				"id":friend_id,
				'name':friend['name'],
				"total":"0/3",
				"on_iris": False
			})
			continue
		today = datetime.today()-timedelta(hours=7)
		last_refreshed = datetime.strptime(user["Item"]['last_refreshed'],'%Y-%m-%d')
		diff = today-last_refreshed
		if diff.days > 6:
			board.append({
				"id":friend_id,
				'name':friend['name'],
				"total": "0/3",
				"on_iris": True
			})
		else:
			total = sum([int(user["Item"]['current_contacts'][e]['contacted']) for e in user["Item"]['current_contacts']])
			board.append({
				"id":friend,
				"total":f"{total}/3"
			})
	user = table.get_item(Key={"user_id":str(user_id)})
	total = sum([int(user["Item"]['current_contacts'][e]['contacted']) for e in user["Item"]['current_contacts']])
	board.append({
		"id":user_id,
		"name":"You",
		"total":f"{total}/3",
		"on_iris":True,
	})
	return sorted(board, key=lambda x: x['total'])[::-1]
	

def update_messaged(table, user_id, update):
	table.update_item(
		Key={
			'user_id':user_id,
		},
		UpdateExpression="SET current_contacts.#u.contacted=:v",
		ExpressionAttributeNames={
			'#u':update,
		},
		ExpressionAttributeValues={
			':v':True,
		}
	)

def refresh_contacts(table, user_id):
	user = table.get_item(Key = {"user_id":str(user_id)})
	if "Item" in user:
		current_contacts = user["Item"]["current_contacts"].keys()
		all_acquaintances = user["Item"]["acquaintances"]
		if len(all_acquaintances) < 3:
			new_contacts = {i['id']:{'contacted':False, 'name':i['name']} for i in all_acquaintances}
		if len(all_acquaintances) > 6:
			new_contacts = {i['id']:{'contacted':False, 'name':i['name']} for i in random.sample([e for e in all_acquaintances if e['id'] not in current_contacts], 3)}
		else:
			new_contacts = {i['id']:{'contacted':False, 'name':i['name']} for i in random.sample([e for e in all_acquaintances if e['id'] not in current_contacts], 3)}
		table.update_item(
			Key={
				'user_id':user_id,
			},
			UpdateExpression="SET current_contacts=:n",
			ExpressionAttributeValues={
				':n':new_contacts,
			}
		)

def event_handler(event, context):
	user_id = event['user_id'][-10:]
	if 'messaged' in event:
		update = event['messaged']
	else:
		update = ""

	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('contacts_experiments_2')

	if update:
		update_messaged(table, user_id, update)

	user = table.get_item(Key = {"user_id":str(user_id)})
	assert "Item" in user

	today = datetime.today()-timedelta(hours=7)
	last_refreshed = datetime.strptime(user["Item"]['last_refreshed'],'%Y-%m-%d')
	diff = today-last_refreshed
	if diff.days>6 or not user["Item"]['current_contacts']:
		refresh_contacts(table, user_id)
		user = table.get_item(Key = {"user_id":str(user_id)})
		assert "Item" in user

	current_contacts = user["Item"]['current_contacts']

	leaderboard = get_leaderboard(
		user_id,
		table,
		user["Item"]['friends']
	)

	ret = {
		'current_contacts':[{"id":k, 'messaged': current_contacts[k]['contacted'], 'name': current_contacts[k]['name']} for k in current_contacts],
		'leaderboard':leaderboard,
	}

	return json.loads(json.dumps(ret))

# def __main__():
# 	print(event_handler({"user_id":"12324565", "messaged":'134546'}, None))

# __main__()