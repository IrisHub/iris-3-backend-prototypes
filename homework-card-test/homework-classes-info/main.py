import boto3
import json

def piazza_get(class_id):
	pass

def create_class(class_id):
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
		ret = {}
		ret['class_name']=course['course_name']
		ret['assignments']={
			e:{
				problem: {
					'num':0,
					'votes':[0,0,0,0],
				} for problem in [f"Question {i}" for i in range(1, 11)]
			} for e in assignments
		}
		return ret


def vote(vote, ctable, utable):
	class_id = vote['class_id']
	assignment_id = vote['assignment_id']
	problem_id = vote['problem_id']
	value = int(vote['value'])
	utable.update_item(
		Key = {
			"user_id":user_id
		},
		UpdateExpression="SET votes.#i=:v",
		ExpressionAttributeNames={
			"#i":f"{class_id}_{assignment_id}_{problem_id}"
		}




def event_handler(event, context):
	user_id = event['user_id']
	user_id = "".join(filter(str.isdigit, str(user_id)))[-10:]
	poll_values = [
		30,
		60,
		120,
		180
	]

	dynamodb = boto3.resource('dynamodb')
	utable = dynamodb.Table('homework_experiments')
	ctable = dynamodb.Table('crowdsourcing')

	if 'vote' in event:
		vote(event['vote'], ctable, utable, user_id)
	else:
		vote = None

	user = utable.get_item(Key={"user_id":user_id})
	assert "Item" in user

	classes = user["Item"]['classes']

	ret = {"classes":[], "polls":[]}
	for c in classes:
		class_ret = {}
		class_id = c['class_id']
		class_ret['class_id'] = class_id
		class_ret['class_name'] = c['class_name']
		class_ret['assignments'] = []
		course = ctable.get_item(Key={"uid":class_id})
		if "Item" not in course:
			ctable.put_item(
				Item={
					"uid":class_id,
					"data":create_class(class_id)
				}
			)
			course = ctable.get_item(Key={"uid":class_id})
		
		assignments = course["Item"]['data']['assignments']
		for i, a in enumerate(assignments.keys()):
			assignment = assignments[a]
			assignment_ret = {}
			total_assignment_time = 0
			total_votes = 0
			assignment_ret['assignment_components'] = []
			for i, p in enumerate(assignment.keys()):
				component_ret = {}
				component_ret['component_id'] = str(i)
				component_ret['component_name'] = p
				problem = assignment[p]
				problem_num = int(problem['num'])
				problem_votes = [int(v) for v in problem['votes']]
				problem_time = sum([poll_values[i]*int(e) for i,e in enumerate(problem_votes)])
				component_ret['component_votes'] = problem_votes
				component_ret['component_avg_time'] = str(int(problem_time/max(problem_num, 1))) + "mins"
				assignment_ret['assignment_components'].append(component_ret)
				total_assignment_time += problem_time
				total_votes += problem_num
			assignment_ret['assignment_components'] = sorted(assignment_ret['assignment_components'], key=lambda x:x['component_id'])

			assignment_avg_time = str(int(total_assignment_time / max(total_votes, 1))) + " mins"
			assignment_ret['assignment_name'] = str(a)
			assignment_ret['assignment_id'] = str(i)
			assignment_ret['assignment_avg_time'] = assignment_avg_time
			class_ret['assignments'].append(assignment_ret)


		ret['classes'].append(class_ret)
	ret['polls'].append(
		[
			{
				"text":"30min",
				"emoji":"😄"
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
	)
	print(ret)
	return ret

def __main__():
	event = {
		"user_id":"+1(949)836-2723"
	}
	context = {}
	print(json.dumps(event_handler(event, context), indent=4))

__main__()






