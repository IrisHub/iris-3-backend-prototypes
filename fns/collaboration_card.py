import boto3
import json
from utils import *
import random

def create_class(class_id):
	dtable = table_init('crowdsource_data')
	with open('course_folders.json', 'r') as f:
		data = json.load(f)['result']
		course = [e for e in data if e['course_id']==class_id and 'course_folders' in e.keys()][0]
		assignments = [e for e in course['course_folders'] 
			if 'midterm' not in e 
			and 'logistics' not in e 
			and 'other' not in e
			and 'exam' not in e
			and "office" not in e
		]
		for i, e in enumerate(assignments):
			metadata = {
				"course_name":course['course_name'],
				"assignment_name":e,
				"assignment_number":i,
			}
			crowdsourced_data_init(dtable, 'collaboration_card', f"{class_id}_{i}", metadata = metadata)

def classes_list(event, context):
	with open('course_folders.json', 'r') as f:
		data = json.load(f)
		classes = [{'class_id':e['course_id'], 'class_name':e['course_name']} for e in data['result'] if 'course_folders' in e]
		return json.loads(json.dumps({"classes":classes}))

def auth(event, context):
	user_id = event['user_id']
	user_id = parse_user(user_id)
	class_ids = event['class_ids']
	class_names = event['class_names']	

	utable = table_init('users')
	dtable = table_init('crowdsource_data')

	user_init(utable, user_id)

	for class_id in class_ids:
		user_follow(utable, user_id, 'collaboration_card', class_id)
		exists = crowdsourced_data_verify(dtable, 'collaboration_card', class_id)
		if not exists:
			create_class(class_id)
		with open('course_folders.json', 'r') as f:
			data = json.load(f)['result']
			course = [e for e in data if e['course_id']==class_id and 'course_folders' in e.keys()][0]
			assignments = [e for e in course['course_folders'] 
				if 'midterm' not in e 
				and 'logistics' not in e 
				and 'other' not in e
				and 'exam' not in e
				and "office" not in e
			]
		for i, assignment in enumerate(assignments):
			update({'class_id':class_id, 'assignment_id':i, 'broadcast_tags':None}, user_id, dtable)

def get_emoji():
	emojis = ['🐵', '🦍', '🐶', '🐺', '🦊', '🐱', '🦁', '🐯', '🐴', '🦄', '🐮', '🐷', '🐐', '🐫', '🦙', '🦒', '🐘', '🦏', '🦛', '🐭', '🐹', '🐰', '🦇', '🐻', '🐨', '🐼', '🦃', '🐔', '🐦', '🐧', '🦉', '🦜', '🐸', '🐲', '🦖', '🐳', '🐬', '🐟', '🐙', '🦋', '🐛', '🐜', '🐝', '🦀']
	animal_names = ['Monkey', 'Gorilla', 'Dog', 'Wolf', 'Fox', 'Cat', 'Lion', 'Tiger', 'Horse', 'Unicorn', 'Cow', 'Pig', 'Goat', 'Camel', 'Llama', 'Giraffe', 'Elephant', 'Rhinoceros', 'Hippopotamus', 'Mouse', 'Hamster', 'Rabbit', 'Bat', 'Bear', 'Koala', 'Panda', 'Turkey', 'Chicken', 'Bird', 'Penguin', 'Owl', 'Parrot', 'Frog', 'Dragon', 'T-Rex', 'Whale', 'Dolphin', 'Fish', 'Octopus', 'Butterfly', 'Bug', 'Ant', 'Honeybee', 'Crab']
	total = len(emojis)
	idx = random.randrange(0, total)
	return (emojis[idx], animal_names[idx])

def update(event, user_id, dtable):
	current_profile = dtable.get_item(Key={'card_name':'collaboration_card', 'data_path':f"{event['class_id']}_{event['assignment_id']}"})["Item"]
	if user_id not in current_profile['crowdsourced_data']:
		emoji, animal = get_emoji()
		animal = f"Anonymous {animal}"
		num = 0
		for uid in current_profile['crowdsourced_data']:
			if animal == uid['broadcast_name']:
				num += 1
		if num != 0:
			animal = f"{animal} {num}"
		update = {"broadcast_icon":emoji, "broadcast_name":animal}
	else:
		update = {
			'broadcast_icon':current_profile['crowdsourced_data'][user_id]['broadcast_icon'],
			'broadcast_name':current_profile['crowdsourced_data'][user_id]['broadcast_name'],
		}

	if not event['broadcast_tags']:
		update['item'] = ""
	else:
		update['item'] = event['broadcast_tags']
	crowdsourced_data_update(dtable, 'collaboration_card', f"{event['class_id']}_{event['assignment_id']}", user_id, update=update)

def collaboration_info(event, context):
	user_id = event['user_id']
	user_id = parse_user(user_id)

	utable = table_init('users')
	dtable = table_init('crowdsource_data')

	if 'class_id' in event and 'assignment_id' in event:
		update(event, user_id, dtable)

	all_data = user_get_card(utable, dtable, user_id, 'collaboration_card')
	class_ids = fetch_user_card_following(utable, user_id, 'collaboration_card')
	ret = {"classes":[]}
	for class_id in class_ids:
		class_ret = {}
		class_ret['class_id']=class_id
		class_broadcasts = [x for x in all_data if class_id in x['data_path']]
		class_ret['class_name'] = class_broadcasts[0]['metadata']['course_name']
		class_ret['assignments'] = []
		# assignments = group_by(class_broadcasts, lambda x: int(x['metadata']['assignment_number']))

		
		for assignment in class_broadcasts:
			assignment_ret = {}
			assignment_ret['assignment_id'] = str(int(assignment['metadata']['assignment_number']))
			assignment_ret['assignment_name'] = assignment['metadata']['assignment_name']

			current_user = assignment['crowdsourced_data'][user_id]
			assignment_ret['current_user_broadcast_icon']= current_user['broadcast_icon']
			assignment_ret['current_user_broadcast_name']= current_user['broadcast_name']
			assignment_ret['current_user_broadcast_tags']= current_user['item']

			other_users = []
			for user_id in assignment['crowdsourced_data']:
				d = {
					'id':user_id,
					'broadcast_name':assignment['crowdsourced_data'][user_id]['broadcast_name'],
					'broadcast_icon':assignment['crowdsourced_data'][user_id]['broadcast_icon'],
					'broadcast_tags':assignment['crowdsourced_data'][user_id]['item'],
				}
				other_users.append(d)
			assignment_ret['other_users'] = other_users
			
			class_ret['assignments'].append(assignment_ret)

		ret["classes"].append(class_ret)

	return(ret)

def __main__():
	classes = classes_list(None, None)['classes']
	class_ids = [e['class_id'] for e in classes[:2]]
	class_names = [e['class_name'] for e in classes[:2]]
	d = {
		'user_id':'1(949)836-2723',
		'class_ids':class_ids,
		'class_names':class_names
	}
	auth(d, None)
	d = {'user_id':'1(949)836-2723',}
	collaboration_info(d, None)
	d = {'user_id':'1(949)836-2723','class_id' :class_ids[0], 'assignment_id':0,'broadcast_tags':None}
	collaboration_info(d, None)
	d = {'user_id':'1(949)836-2723','class_id' :class_ids[0], 'assignment_id':0,'broadcast_tags':"1A"}
	collaboration_info(d, None)
	d = {'user_id':'1(949)836-2723','class_id' :class_ids[0], 'assignment_id':0,'broadcast_tags':None}
	collaboration_info(d, None)
	d = {'user_id':'1(949)836-2723','class_id' :class_ids[0], 'assignment_id':0,'broadcast_tags':"2B"}
	collaboration_info(d, None)
	d = {'user_id':'1(949)836-2723','class_id' :class_ids[0], 'assignment_id':0,'broadcast_tags':"SLKDFJKLSDJFSDF I'M GOING TO SCREAM"}
	collaboration_info(d, None)

__main__()
