import boto3

def event_handler(event, context):
	print(event)
	user_id = event['user_id']
	friend_ids = event['friend_ids']
	friend_names = event['friend_names']
	refresh_token = event['refresh_token']

	filt = lambda s: "".join(filter(str.isdigit, s))[-10:]
	user_id = filt(user_id)
	friend_ids = [filt(f) for f in friend_ids]
	

	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('contacts_experiments')

	friend_refresh = []
	for friend in friend_ids:
		# Check if your friends are already in the database. If they are, add their refresh token and add yourself to their "added_by";
		# otherwise, create an entry for them
		res = table.get_item(Key={"user_id":str(friend)})
		if 'Item' in res:
			friend_refresh.append(res['Item']['refresh_token'])
			table.update_item(
				Key = {
					'user_id':friend,
				},
				UpdateExpression="SET added_by=list_append(added_by, :u)",
				ExpressionAttributeValues={
					':u':[user_id],
				}
			)
		else:
			friend_refresh.append("")
			table.put_item(
				Item = {
					'user_id':friend,
					'refresh_token':"",
					'friends':{},
					'added_by':[user_id]
				})

	friends = {e[0]:{"name":e[1], "refresh_token": e[2]} for e in list(zip(friend_ids, friend_names, friend_refresh))}

	# Check if you are already in the database. If you are, add your refresh token to each of your friends. If not, create user
	user = table.get_item(Key={"user_id":str(user_id)})
	if "Item" in user:
		print(f"{user_id} was added by {str(user['Item']['added_by'])}")
		for friend in user['Item']['added_by']:
			print(table.get_item(Key={"user_id":friend}))
			table.update_item(
				Key={
					'user_id':friend,
				},
				UpdateExpression="SET friends.#i.refresh_token=:r",
				ExpressionAttributeValues={
					':r':refresh_token,
				},
				ExpressionAttributeNames={
					'#i':user_id,
				}
			)
		table.update_item(
			Key={
				'user_id':user_id,
			},
			UpdateExpression="SET friends=:f, refresh_token=:r",
			ExpressionAttributeValues={
				':f':friends,
				':r':refresh_token,
			}
		)
	else:
		table.put_item(
			Item={
				'user_id':user_id,
				'friends':friends,
				'refresh_token':refresh_token,
				'added_by':[]
			})

# def __main__():
# 	event_handler({'user_id':"1", "friend_ids":["2","3"], "refresh_token":"1//06C7VoeUCs5mwCgYIARAAGAYSNwF-L9IrfA_h7xnF_rBP4uddFOANfOm10RoCA1bx14wAptAnnURlnAsYTCHzwsYgbPPX_cxl7dI"}, None)
# 	event_handler({'user_id':"2", "friend_ids":["1"], "refresh_token":"B"}, None)
# 	event_handler({'user_id':"4", "friend_ids":["3"], "refresh_token":"C"}, None)

# __main__()
 