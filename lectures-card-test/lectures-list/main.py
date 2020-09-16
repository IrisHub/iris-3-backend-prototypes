import json
import os
import requests

url = "https://berkeleytime.com/api/catalog/catalog_json/"
classes = requests.get(url).json()['courses']


def check(dept, num):
	flag = False
	for e in classes:
		if e['abbreviation'] == dept and e['course_number'] == num:
			flag = True
			break

	if not flag:
		print(f"No match found for {dept} {num}")

with open("course_folders.json", 'r+') as f:
	data = json.load(f)
	for d in data['result']:
		if 'course_folders' in d:
			course_name = d['course_name']
			course_num = course_name.split(":")[0]
			try:
				dept = course_num.rsplit(" ", 1)[0]
				num = course_num.rsplit(" ", 1)[1]
				check(dept, num)
			except:
				continue

