import boto3
from utils import *
import time

def message_friend(utable, user_id, friend_id):
	user_social_modify(utable, user_id, 'reminders_card', [friend_id, 'messaged'], True)
	user_social_modify(utable, user_id, 'reminders_card', [friend_id, 'last_contacted'], int(time.time()))

def reset_friend(utable, user_id, friend_id):
	user_social_modify(utable, user_id, 'reminders_card', [friend_id, 'messaged'], False)
	return False

def change_frequency(utable, user_id, friend_id, new_frequency):
	user_social_modify(utable, user_id, 'reminders_card', [friend_id, 'frequency'], new_frequency)

def auth(event, context):
	user_id = event['user_id']
	user_id = parse_user(user_id)
	friend_ids = event['friend_ids']
	friend_ids = [parse_user(i) for i in friend_ids]
	friend_names = event['friend_names']

	utable = table_init('users')
	user_init(utable, user_id)
	data = {
		f[0]: {
			"frequency": 0,
			"name": f[1],
			"messaged": False,
			"last_contacted":int(time.time())
		} for f in list(zip(friend_ids, friend_names))
	}
	user_social_add(utable, user_id, 'reminders_card', data)

def get_info(event, context):
	user_id = event['user_id']
	user_id = parse_user(user_id)
	utable = table_init('users')

	ret = {}
	ret['options'] = [
		'Daily',
		'Every few days',
		'Weekly',
		'Every 2 Weeks',
	]
	day = 86400 + 7200
	few_days = day * 3
	weekly = day * 7
	every_two_weeks = weekly * 2
	durations = [
		day,
		few_days,
		weekly,
		every_two_weeks
	]

	if event['friend_id']:
		if event['frequency']:
			new_frequency = ret['options'].index(new_frequency)
			change_frequency(utable, user_id, event['friend_id'], new_frequency)
		else:
			message_friend(utable, user_id, event['friend_id'])

	ret['friend_states'] = []
	user_info = utable.get_item(Key={'user_id':user_id})
	friends = user_info['Item']['social']['reminders_card']
	oski_state = 0
	for friend_id in friends:
		d = {}
		time_since_last = int(time.time()) - int(friends[friend_id]['last_contacted'])
		duration = durations[int([friends][friend_id]['frequency'])]
		if time_since_last > 0.75* duration:
			d['messaged'] = reset_friend(utable, user_id, friend_id)
			oski_state = max(1, oski_state)
			if time_since_last > duration:
				oski_state = max(2, oski_state)
		else:
			d['messaged'] = friends[friend_id]['messaged']
		d['id'] = friend_id
		d['name'] = friends[friend_id]['name']
		d['frequency'] = ret['options'][int([friends][friend_id]['frequency'])]
		ret['friend_states'].append(d)

	ret['friend_states'] = sorted(ret['friend_states'], lambda x: x['messaged'])

	oski_healths = [
		'VIBING',
		'UNWELL',
		'DEAD'
	]
	ret['oski_state'] = {
		'health': oski_healths[oski_state]
		'img': f"https://oski-pics.s3-us-west-1.amazonaws.com/oski{oski_state}.png"
	}

	return ret

	return ret