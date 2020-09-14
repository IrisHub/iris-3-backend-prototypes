import boto3
import json

def event_handler(event, context):
	user_id = event['user_id']
	user_id = "".join(filter(str.isdigit, str(user_id)))[-10:]
	classes = event['classes']

	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('homework_experiments')

	table.put_item(
		Item = {
			'user_id':user_id,
			'classes':classes,
			'votes':{},
		}
	)

def __main__():
	event = {
		"user_id":"+1 (949)836-2723",
		"classes": [
			{
            	"class_id": "kekbytt9day4d7",
            	"class_name": "MATH 126: Introduction to Partial Differential Equations (Fall 2020)"
        	},
        	{
	            "class_id": "kek4ylgpb4y78y",
	            "class_name": "113: Math 113 - LEC 003: Introduction to abstract algebra"
	        },
	        {
	            "class_id": "kehj56sr5vj4v3",
	            "class_name": "MATH 142: Elementary Algebraic Topology"
	        },
		]
	}
	context = {}
	print(json.dumps(event_handler(event, context), indent=4))

__main__()
