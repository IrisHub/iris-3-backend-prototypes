import boto3
import json

def piazza_get(class_id):
	pass

def create_class(class_id):
	with open('course_folders.json', 'r') as f:
		data = json.load(f)['result']
		course = [c for c in data if e['course_id']==class_id and 'course_folders' in e.keys()][0]
		assignments = [e for e in course['course_folders'] 
			if 'midterm' not in e 
			and 'logistics' not in e 
			and 'other' not in e
			and 'exam' not in e
			and "office" not in e
		]
		ret = {}
		ret['class_name']=course['course_name']
		ret['assignments'] = {}
		for i, e in enumerate(assignments):
			ret['assignments'][str(i)] = {
				'name':e,
			}
			for j, f in enumerate([f"Question {i}" for i in range(1, 11)]):
				ret['assignments'][str(i)][str(j)] = {
					'name': f,
					'num':0,
					'votes':[0, 0,0,0]
				}
		return ret


def user_vote(vote, ctable, utable, user_id):
	class_id = vote['class_id']
	assignment_id = vote['assignment_id']
	problem_id = vote['problem_id']
	value = int(vote['value'])
	curr_votes = ctable.get_item(Key={"uid":class_id})['Item']['data']['assignments'][assignment_id][component_id]
	if value != -1:
		curr_votes[value]+=1
	else:
		current_user_vote = int(utable.get_item(Key={"user_id":user_id})['Item']['votes'][f"{class_id}_{assignment_id}_{problem_id}"])
		curr_votes[current_user_vote]-=1
	
	print(curr_votes)
	ctable.update_item(
		Key = {
			"uid":class_id,
		},
		UpdateExpression="SET data.assignments.#a.#c=:v",
		ExpressionAttributeNames={
			"#a":assignment_id,
			"#c":component_id
		},
		ExpressionAttributeValues={
			":v":curr_votes
		}
	)
	utable.update_item(
		Key = {
			"user_id":user_id
		},
		UpdateExpression="SET votes.#i=:v",
		ExpressionAttributeNames={
			"#i":f"{class_id}_{assignment_id}_{problem_id}"
		},
		ExpressionAttributeValues={
			":v":value
		}
	)




def event_handler(event, context):
	user_id = event['user_id']
	user_id = "".join(filter(str.isdigit, str(user_id)))[-10:]
	poll_values = [
		30,
		60,
		120,
		180,
	]

	dynamodb = boto3.resource('dynamodb')
	utable = dynamodb.Table('homework_experiments')
	ctable = dynamodb.Table('crowdsourcing')

	if 'class_id' in event and 'assignment_id' in event and 'problem_id' in event and 'value' in event:
		if event['class_id'] and event['assignment_id'] and event['problem_id'] and event['value']:
			user_vote({'vote':{
				'class_id':event['class_id'],
				'assignment_id':event['assignment_id'],
				'problem_id':event['problem_id'],
				'value':event['value']
			}}, ctable, utable, user_id)
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
		for assignment_id in sorted(assignments.keys()):
			assignment = assignments[assignment_id]
			assignment_ret = {}
			# assignment_ret['order'] = str(assignment['order'])
			total_assignment_time = 0
			total_votes = 0
			assignment_ret['assignment_components'] = []
			for problem_id in sorted(assignment.keys()):
				component_ret = {}
				component_ret['component_id'] = problem_id
				problem = assignment[problem_id]
				component_ret['component_name'] = problem['name']
				# component_ret['order'] = str(problem['order'])
				problem_num = int(problem['num'])
				problem_votes = [int(v) for v in problem['votes']]
				problem_pct = [int(100*e/problem_num) for e in problem_votes]
				problem_time = sum([poll_values[i]*int(e) for i,e in enumerate(problem_votes)])
				component_ret['component_votes'] = problem_votes
				component_ret['component_avg_time'] = "0" if problem_num == 0 else (str(int(problem_time/problem_num)) + "mins")
				component_ret['component_vote_pcts'] = problem_pct
				assignment_ret['assignment_components'].append(component_ret)
				total_assignment_time += problem_time
				total_votes += problem_num
				if f"{class_id}_{str(i)}_{str(j)}" in user['Item']['votes']:
					assignment_ret['user_vote'] = user['Item']['votes'][f"{class_id}_{str(i)}_{str(j)}"]
				else:
					assignment_ret['user_vote'] = -1

			assignment_ret['assignment_components'] = sorted(assignment_ret['assignment_components'], key=lambda x:x['component_id'])

			assignment_avg_time = "0" if total_votes == 0 else (str(int(total_assignment_time / total_votes)) + " mins")
			assignment_ret['assignment_name'] = assignment['name']
			assignment_ret['assignment_id'] = assignment_id
			assignment_ret['assignment_avg_time'] = assignment_avg_time
			class_ret['assignments'].append(assignment_ret)


		ret['classes'].append(class_ret)
	
	ret['polls'].append(
		[
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
	)
	# print(ret)
	return ret

# def __main__():
# 	event = {
# 		"user_id":"+1(949)836-2723",
# 		"vote": {

# 		}
# 	}
# 	context = {}
# 	print(json.dumps(event_handler(event, context), indent=4))

# __main__()
