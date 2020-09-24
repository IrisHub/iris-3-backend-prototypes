import os
import json
import boto3
from itertools import groupby

def group_by(lst, keyfunc):
	# Groups a list of dicts by the given keyfunc, and returns a corresponding array
	lst = sorted(lst, key=keyfunc)
	r = []
	for key, group in groupby(lst, keyfunc):
		r.append(list(group))

	return r

def parse_user(user_id):
	return "".join(filter(str.isdigit, str(user_id)))[-10:]

def table_init(table_name):
	# Grab the DynamoDB table based on table_name
	dynamodb = boto3.resource('dynamodb')
	return dynamodb.Table(table_name)

def crowdsourced_data_verify(dtable, card_name, p_data_path):
	x = partial_query(dtable, card_name, p_data_path)
	return bool(x)

def user_init(utable, user_id):
	user_id = parse_user(user_id)
	user = utable.get_item(Key={"user_id":user_id})
	if not "Item" in user:
		utable.put_item(
			Item = {
				'user_id':user_id,
				'crowdsourcing':{},
				'social':{},
			}
		)

def fetch_user_card_following(utable, user_id, card_name):
	user_id = parse_user(user_id)
	following_list = utable.get_item(Key={"user_id":user_id})
	return following_list['Item']['crowdsourcing'][card_name].split("|")


def crowdsourced_data_init(dtable, card_name, data_path, metadata={}):
	# Create a new entry in the crowdsourcing table
	temp = dtable.get_item(
		Key={
			"card_name":card_name,
			"data_path":data_path,
		}
	)
	if "Item" in temp:
		return

	dtable.put_item(
		Item = {
			"card_name":card_name,
			"data_path":data_path,
			"metadata":metadata,
			"crowdsourced_data":{}
		}
	)

def crowdsourced_data_update_metadata(dtable, card_name, data_path, metadata):
	dtable.update_item(
		Key = {
			"card_name":card_name,
			"data_path":data_path,
		},
		UpdateExpression = "SET metadata=:m",
		ExpressionAttributeValues = {
			":m":metadata,
		}
	)

def crowdsourced_data_update(dtable, card_name, data_path, user_id="", update=None, meta=False):
	# Update the crowdsourcing table entry at the user id with the edit value
	# If update is none, remove the user's vote
	# If metadata is True, replace the metadata with the value in the update field
	# At least one of `user_id` or `metadata` must be truthy
	# If meta is True, update must be non-null
	assert meta or user_id
	if meta:
		assert update
		crowdsourced_data_update_metadata(dtable, card_name, data_path, update)
		
	else:
		if not update:
			crowdsourced_data_remove(dtable, card_name, data_path, user_id)
		else:
			dtable.update_item(
				Key = {
					"card_name":card_name,
					"data_path":data_path,
				},
				UpdateExpression = "SET crowdsourced_data.#u=:d",
				ExpressionAttributeNames = {
					'#u':user_id,
				},
				ExpressionAttributeValues = {
					':d':update,
				}
			)


def crowdsourced_data_remove(dtable, card_name, data_path, user_id):
	# Remove the user's input from that particular crowdsourcing table
	dtable.update_item(
		Key = {
			"card_name":card_name,
			"data_path":data_path,
		},
		UpdateExpression = "REMOVE crowdsourced_data.#u",
		ExpressionAttributeNames = {
			'#u':user_id
		}
	)

def user_follow(utable, user_id, card_name, partial_queries):
	# Save a partial query to a user's profile; the queries are a | delimited string
	utable.update_item(
		Key = {
			"user_id":user_id,
		},
		UpdateExpression = "SET crowdsourcing.#c=:i",
		ExpressionAttributeNames = {
			"#c":card_name,
		},
		ExpressionAttributeValues = {
			":i":partial_queries
		}
	)

def user_social_add(utable, user_id, card_name, value):
	utable.update_item(
		Key = {
			'user_id':user_id,
		},
		UpdateExpression = "SET social.#c = :v",
		ExpressionAttributeNames = {
			"#c":card_name,
		},
		ExpressionAttributeValues = {
			":v":value
		}
	)

def user_social_modify(utable, user_id, card_name, data_path, data):
	path = '.'.join(data_path)
	d = { f"#i{j}": d for j, d in enumerate(data_path)}
	path = '.'.join(sorted(d.keys()))
	update_expr = f'SET social.{card_name}.{path} = :d'
	print(update_expr)
	utable.update_item(
		Key = {
			'user_id':user_id,
		},
		UpdateExpression = update_expr,
		ExpressionAttributeNames = d,
		ExpressionAttributeValues = {
			":d":data
		}
	)



def partial_query(table, card_name, p_data_path):
	# Given a rank key, hash key, and partial query, return the items retrieved by a query on hash_key with filter rank_key
	items = table.query(
		KeyConditionExpression = "card_name = :c AND begins_with(data_path, :p)",
		ExpressionAttributeValues = {
			":c":card_name,
			":p":p_data_path
		}
	)
	return items["Items"]

def user_get_card(utable, dtable, user_id, card_name):
	# Get the raw database data for a specific card for a specific user
	user = utable.get_item(Key={'user_id':user_id})
	p_data_paths = user['Item']['crowdsourcing'][card_name].split("|")

	items = []
	for p in p_data_paths:
		items.extend(partial_query(dtable, card_name, p))

	return items

