import boto3
import json

def event_handler(event, context):
	with open('course_folders.json', 'r') as f:
		data = json.load(f)
		classes = [{'class_id':e['course_id'], 'class_name':e['course_name']} for e in data['result'] if 'course_folders' in e]
		return json.loads(json.dumps({"classes":classes}))

def __main__():
	event = {}
	context = {}
	print(json.dumps(event_handler(event, context), indent=4))

__main__()