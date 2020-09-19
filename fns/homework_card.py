import boto3
from utils import *

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
			for j, f in enumerate([f"Question {i}" for i in range(1, 11)]):
				metadata = {
					"course_name":course['course_name'],
					"assignment_name":e,
					"assignment_number":i,
					"problem_name":f,
					"problem_number":j,
				}
				crowdsourced_data_init(dtable, 'homework_card', f"{class_id}_{i}_{j}", metadata = metadata)

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
		user_follow(utable, user_id, 'homework_card', class_id)
		exists = crowdsourced_data_verify(dtable, 'homework_card', class_id)
		if not exists:
			create_class(class_id)


def classes_info(event, context):
	user_id = event['user_id']
	user_id = parse_user(user_id)

	utable = table_init('users')
	dtable = table_init('crowdsource_data')

	if 'class_id' in event and 'assignment_id' in event and 'problem_id' in event:
		if int(event['value']) < 0:
			update = None
		else:
			update = {"item":event['value']}	
		crowdsourced_data_update(dtable, 'homework_card', f"{event['class_id']}_{event['assignment_id']}_{event['problem_id']}", user_id, update=update)

	all_data = user_get_card(utable, dtable, user_id, 'homework_card')
	class_ids = fetch_user_card_following(utable, user_id, 'homework_card')
	ret = {"classes":[], "polls":[]}
	for class_id in class_ids:
		class_ret = {}
		class_ret['class_id']=class_id
		class_polls = [x for x in all_data if class_id in x['data_path']]
		class_ret['class_name'] = class_polls[0]['metadata']['course_name']
		class_ret['assignments'] = []
		assignments = group_by(class_polls, lambda x: int(x['metadata']['assignment_number']))

		for assignment in assignments:
			a0 = assignment[0]
			assignment_ret = {}
			assignment_ret['assignment_id'] = str(int(a0['metadata']['assignment_number']))
			assignment_ret['assignment_name'] = a0['metadata']['assignment_name']

			total_votes, total_assignment_time = 0, 0
			assignment_ret['assignment_components'] = []
			for problem in assignment:
				poll_default = [0, 0, 0, 0]
				poll_eval = [30, 60, 120, 180]
				component_ret = {}
				# print(problem)
				component_ret['component_id'] = str(int(problem['metadata']['problem_number']))
				component_ret['component_name'] = problem['metadata']['problem_name']
				if not problem['crowdsourced_data']:
					problem_num = 0
					problem_votes = poll_default
					problem_pct = [0, 0, 0, 0]
					problem_time = 0
				else:
					problem_num = len(problem['crowdsourced_data'].keys())
					for user in problem['crowdsourced_data']:
						poll_default[int(problem['crowdsourced_data'][user]['item'])] += 1
					problem_votes = poll_default
					problem_pct = [int(100*e/problem_num) for e in problem_votes]
					problem_time = sum([poll_eval[i]*int(e) for i,e in enumerate(problem_votes)])
				component_ret['component_votes'] = problem_votes
				component_ret['component_avg_time'] = "0" if problem_num == 0 else (str(int(problem_time/problem_num)) + "mins")
				component_ret['component_vote_pcts'] = problem_pct
				if user_id in problem['crowdsourced_data']:
					component_ret['user_vote'] = int(problem['crowdsourced_data'][user_id]['item'])
				else:
					component_ret['user_vote'] = -1
				assignment_ret['assignment_components'].append(component_ret)
				total_assignment_time += problem_time
				total_votes += problem_num
			
			assignment_ret['assignment_components'] = sorted(assignment_ret['assignment_components'], key=lambda x:x['component_id'])
			assignment_avg_time = "0" if total_votes == 0 else (str(int(total_assignment_time / total_votes)) + " mins")
			assignment_ret['assignment_avg_time'] = assignment_avg_time
			
			class_ret['assignments'].append(assignment_ret)
		ret['classes'].append(class_ret)

	poll = [
		{
			"text":"30min",
			"icon":"😄"
		},
		{
			"text":"1hr",
			"icon":"🙂"
		},
		{
			"text":"2hrs",
			"icon":"😕"
		},
		{
			"text":"3hrs",
			"icon":	"😵"
		}
	]
	ret['polls'].append(poll)

	return(ret)


def __main__():
	classes = classes_list(None, None)['classes']
	class_ids = [e['class_id'] for e in classes[:2]]
	class_names = [e['class_name'] for e in classes[:2]]
	d = {'user_id':'1(949)836-2723',
		'class_ids':class_ids,
		'class_names':class_names
	}
	auth(d, None)
	d = {'user_id':'1(949)836-2723',}
	classes_info(d, None)
	d = {'user_id':'1(949)836-2723','class_id' :class_ids[0], 'assignment_id':0,'problem_id':0,'broadcast_tags':None}
	classes_info(d, None)
	d = {'user_id':'1(949)836-2723','class_id' :class_ids[0], 'assignment_id':0,'problem_id':0,'broadcast_tags':1}
	classes_info(d, None)
	d = {'user_id':'1(949)836-2723','class_id' :class_ids[0], 'assignment_id':0,'problem_id':0,'broadcast_tags':None}
	classes_info(d, None)
	d = {'user_id':'1(949)836-2723','class_id' :class_ids[0], 'assignment_id':0,'problem_id':0,'broadcast_tags':3}
	classes_info(d, None)
	d = {'user_id':'1(949)836-2723','class_id' :class_ids[0], 'assignment_id':0,'problem_id':0,'broadcast_tags':2}
	classes_info(d, None)

__main__()