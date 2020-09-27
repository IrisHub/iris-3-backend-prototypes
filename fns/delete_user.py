import boto3
from utils import *

def delete(event, context):
	# set_debug(event)
	user_id = event['user_id']
	user_id = parse_user(user_id)

	dtable = table_init('crowdsource_data')
	utable = table_init('users')

	print(user_id)
	user_info = utable.get_item(Key = {'user_id':user_id})
	print(user_info)
	assert "Item" in user_info
	user_info = user_info['Item']
	for card in user_info['crowdsourcing']:
		crowdsourced_data_remove(utable, dtable, card, user_id)
	user_remove(utable, user_id)

# def __main__():
# 	delete({'user_id':'8182033202'}, None)

# __main__()