import json
import requests

url = "https://berkeleytime.com/api/catalog/catalog_json/"
course_url = "https://berkeleytime.com/api/catalog/catalog_json/course_box"
classes = requests.get(url).json()['courses']

course_info = []
for e in classes:
	course_id = e['id']
	course_number = f"{e['abbreviation']} {e['course_number']}"
	try:
		course_data = requests.get(f"{course_url}?course_id={course_id}").json()
	except:
		continue
	course_name = course_data['course']['title']
	course_time = course_data['sections'][0]['word_days']
	if course_data['ongoing']:
		course_info.append({
			"course_name":f"{course_number}: {course_name}",
			"course_id":course_id,
			"course_days":course_time
			})
d = {"result":course_info}
with open('course_times.json', 'r+') as f:
	f.seek(0)
	f.write(json.dumps(d, indent=4))
	f.truncate()

