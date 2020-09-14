import boto3 
from datetime import datetime
from datetime import timedelta

def event_handler(event, context):
	user_id = event['user_id']
	friend_ids = event['close_friend_ids']
	friend_names = event['close_friend_names']
	acquaintance_ids = event['distant_friend_ids']
	acquaintance_names = event['distant_friend_names']

	filt = lambda s: "".join(filter(str.isdigit, s))[-10:]
	user_id = filt(user_id)
	friend_ids = [filt(f) for f in friend_ids]
	acquaintance_ids = [filt(a) for a in acquaintance_ids]

	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('contacts_experiments_2')

	table.put_item(
		Item = {
			'user_id':user_id,
			'friends':list({"id":e[0], "name":e[1]} for e in list(zip(friend_ids, friend_names))),
			'acquaintances':list({"id":e[0], "name":e[1]} for e in list(zip(acquaintance_ids, acquaintance_names))),
			'last_refreshed':(datetime.today()-timedelta(hours=7)-timedelta(7+((datetime.today().weekday()+1) % 7)-6)).strftime('%Y-%m-%d'),
			'current_contacts':{}
		})


# def __main__():
# 	event_handler({
# 		'user_id':"12324565",
# 		'close_friend_ids':['1223','34634','23423'],
# 		'close_friend_names':["Shalom Shablom", "SKREEEE", "VERY HONGRY"],
# 		'distant_friend_ids':['6245545','345265','134546','2346252643'],
# 		'distant_friend_names':['ALSKDJF', 'dfklsjdlkfjf', 'slkdf', 'qlkesd'],
# 		}, None)

# __main__()