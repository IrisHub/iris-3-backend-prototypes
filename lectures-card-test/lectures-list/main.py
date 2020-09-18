import json
import os
import requests

url = "https://berkeleytime.com/api/catalog/catalog_json/"
classes = requests.get(url).json()['courses']

classes_parsed = {
	"course_id":e['id'],
	"course_name":f"{e['abbreviation']} {e['course_number']}: {e['title']}"
for e in classes}

