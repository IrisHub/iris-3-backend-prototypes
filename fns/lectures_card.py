import boto3
from utils import *

def create_class(class_id):
	dtable = table_init('crowdsource_data')
	with open('course_folders.json', 'r') as f:
		data = json.load(f)['result']
		course = [e for e in data if e['course_id']==class_id and 'course_folders' in e.keys()][0]
		for i, e in enumerate([f"Lecture {i}" forr i in range(1, 35)]):
			metadata = {
				"course_name":course['course_name'],
				"lecture_name":e,
				"lecture_number":i,
			}
			crowdsourced_data_init(dtable, 'lectures_card', f"{class_id}_difficulty_{i}", metadata = metadata)
			crowdsourced_data_init(dtable, 'lectures_card', f"{class_id}_recommend_{i}", metadata = metadata)

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
		exists = crowdsourced_data_verify(dtable, 'lectures_card', class_id)
		if not exists:
			create_class(class_id)

	class_ids = "|".join(class_ids)
	user_follow(utable, user_id, 'lectures_card', class_ids)

def lecture_info(event, context):
	user_id = event['user_id']
	user_id = parse_user(user_id)

	utable = table_init('users')
	dtable = table_init('crowdsource_data')

	if 'class_id' in event and 'lecture_id' in event and 'poll_id' in event:
		if int(event['value']) < 0:
			update = None
		else:
			update = {"item":event['value']}
		if event['poll_id']	== 0:
			poll_id = "difficulty"
		else:
			poll_id = "recommend"
		crowdsourced_data_update(dtable, 'homework_card', f"{event['class_id']}_{poll_id}_{event['lecture_id']}", user_id, update=update)

	all_data = user_get_card(utable, dtable, user_id, 'lectures_card')
	class_ids = fetch_user_card_following(utable, user_id, 'lectures_card')
	ret = {"classes":[]}
	for class_id in class_ids:
		class_ret = {}
		class_ret['class_id']=class_id
		class_lectures = [x for x in all_data if class_id in x['data_path']]
		class_ret['class_name'] = class_lectures[0]['metadata']['course_name']
		class_ret['lectures'] = []
		lecture_polls = group_by(class_polls, lambda x: int(x['metadata']['lecture_number']))

		for lecture in lecture_polls:
			l0 = lecture[0]
			lecture_ret = {}
			lecture_ret['lecture_id'] = str(int(l0['metadata']['lecture_number']))
			lecture_ret['lecture_name'] = l0['metadata']['lecture_name']

			poll_difficulty = [0,0,0]
			poll_recommend=[0,0]
			lecture_max_votes = []
			lecture_vote_pcts = []
			user_difficulty_vote, user_recommend_vote = -1, -1
			for poll in lecture:
				if not poll['crowdsourced_data']
					lecture_max_votes.append(0)
					lecture_vote_pcts.append(0)
				else:
					for user in lecture['crowdsourced_data']
						if 'difficulty' in lecture['data_path']:
							poll_difficulty[int(lecture['crowdsourced_data'][user]['item'])] += 1
							if user == user_id:
								user_difficulty_vote = int(lecture['crowdsourced_data'][user]['item'])
						elif 'recommend' in lecture['data_path']:
							poll_recommend[int(lecture['crowdsourced_data'][user]['item'])] += 1
							if user == user_id:
								user_recommend_vote = int(lecture['crowdsourced_data'][user]['item'])
			lecture_max_votes.append(poll_difficulty.index(max(poll_difficulty)))
			lecture_max_votes.append(poll_recommend.index(max(poll_recommend)))
			lecture_vote_pcts.append(int(poll_difficulty/sum(poll_difficulty) * 100))
			lecture_vote_pcts.append(int(poll_recommend/sum(poll_recommend) * 100))

			lecture_ret['lecture_polls'] = [poll_difficulty, poll_recommend]
			lecture_ret['lecture_max_votes'] = lecture_max_votes
			lecture_ret['lecture_vote_pcts'] = lecture_vote_pcts
			lecture_ret['user_vote'] = [user_difficulty_vote, user_recommend_vote]
			
			class_ret['lectures'].append(lecture_ret)

		ret["classes"].append(class_ret)

	poll = [
		{
			"text":"Easy",
			"icon":"😄"
		},
		{
			"text":"Medium",
			"icon":"😕"
		},
		{
			"text":"Hard",
			"icon":	"😵"
		}
	]
	ret['polls'].append(poll)
	poll = [
		{
			"text":"Yes",
			"icon":"😄"
		},
		{
			"text":"No",
			"icon":	"😵"
		}
	]
	ret['polls'].append(poll)

	return(ret)