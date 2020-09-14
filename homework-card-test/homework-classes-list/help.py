import os
import time
import json
import requests
import re

headers_enroll = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'CSRF-Token': '6cov6wa7Ac7fNjQHVTRNC32a',
    'DNT': '1',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
    'Content-Type': 'application/json',
    'Origin': 'https://piazza.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://piazza.com/signup/berkeley',
    'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
}

headers_remove = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'CSRF-Token': '6cov6wa7Ac7fNjQHVTRNC32a',
    'DNT': '1',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
    'Content-Type': 'application/json; charset=UTF-8',
    'Origin': 'https://piazza.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://piazza.com/account_settings',
    'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
}

params_enroll = (
    ('method', 'network.join'),
    ('aid', 'kf0bgbgfqblr'),
)

cookies_enroll = cookies = {
    'session_id': '6cov6wa7Ac7fNjQHVTRNC32a',
    'last_piaz_user': 'j6lew5604hz2li',
    '_ga': 'GA1.2.1667166114.1598380832',
    '_gid': 'GA1.2.1530868759.1599947644',
    'AWSELB': '732545B312943CE3A5A159C88B79D008FE4AE6530D908A737F8EDAF7A299BB9A6DC368FC85BDE1783DE61A9BBCED6DF4B66026BB7C5D23AC87D809FE3C293EA15EEB6C40E7',
    'AWSELBCORS': '732545B312943CE3A5A159C88B79D008FE4AE6530D908A737F8EDAF7A299BB9A6DC368FC85BDE1783DE61A9BBCED6DF4B66026BB7C5D23AC87D809FE3C293EA15EEB6C40E7',
    'piazza_session': '1.eyJleHBpcmVzIjoxNjAxMTYzNjc2LCJwZXJtIjoiMCIsImxvZ2dpbmdfaW4iOnRydWUsImNyZWF0ZWRfYXQiOjE1OTk5NTQwNzYsIndoZW4iOjE1OTk5NTQwNzYsImhvbWUiOiIvIiwicmVtZW1iZXIiOiJvbiIsInNlc3Npb25fdG9rZW4iOiJzdF9yQ0MrMmRqcmZaTnBNVEg3QnNwVCIsIm5pZHMiOiJrZTNzanNwZG1udDY1cjowO2o2aDJjZGt5NXprN2M2OjA7ajV6cDhlc2VjbTMxcnI6MDtpeXdxdzY2cm5iNGhzOjA7ajlqMHVkcnhqanA3NTg6MDtqY2NxM2QzOWRremV1OjA7amM0ZWQyczhjM3YzZnU6MDtqYzhucDEzMDdtMzRoYTowO2ppYTBtcG5waWxsNTl5OjA7amhhZGx0dXI1OXd0dTowO2h5cTBicjF1M2t4N2RnOjA7amtzMzNkNjgzOWk1Y286MDtqbDJubDE3ZzNybDdwZjowO2psMnc4dmg0bGEzMTA1OjA7anFmZWJsazdlcWgxMms6MDtqcXR5cjNxNHJ5bzR6MzowO2p6M25ydWQ1YmltNXRkOjA7anpkYzg0MGh3bWQ3ZGM6MDtrNW5odHdscWJ0YTYybDowO2s1bmRvNzAyOTRxNWZtOjA7azVqMmswZm56ajkxdmg6MDtrNThzYWd6NW12bzUxNDowO2s3dmgydDlyZWNkNXQ4OjA7a2VlajdvcTNhbzQ3YXA6MDsiLCJ0YWciOiIiLCJ1c2VyIjoiajZsZXc1NjA0aHoybGkiLCJlbWFpbCI6ImtydGhha2VyMTIyNEBiZXJrZWxleS5lZHUifQ%3D%3D.aEZ7YUKKz%2BynSWJYhhyM8MLHjp8isANry9kLaD%2Fh3L4%3D',
    '_gat_UA-21514163-1': '1',
}

cookies_remove = {
    'session_id': '6cov6wa7Ac7fNjQHVTRNC32a',
    'last_piaz_user': 'j6lew5604hz2li',
    '_ga': 'GA1.2.1667166114.1598380832',
    '_gid': 'GA1.2.1090627222.1599809848',
    'AWSELB': '732545B312943CE3A5A159C88B79D008FE4AE6530DEA647084583F9DF0336A93698216B8DD368017BA95BD4B2C8ED5B91389E17CAD5D23AC87D809FE3C293EA15EEB6C40E7',
    'AWSELBCORS': '732545B312943CE3A5A159C88B79D008FE4AE6530DEA647084583F9DF0336A93698216B8DD368017BA95BD4B2C8ED5B91389E17CAD5D23AC87D809FE3C293EA15EEB6C40E7',
    'piazza_session': '1.eyJleHBpcmVzIjoxNjAxMDk5MjQzLCJwZXJtIjoiMCIsImxvZ2dpbmdfaW4iOnRydWUsImNyZWF0ZWRfYXQiOjE1OTk4ODk2NDMsIndoZW4iOjE1OTk4ODk2NDMsImhvbWUiOiIvIiwicmVtZW1iZXIiOiJvbiIsInNlc3Npb25fdG9rZW4iOiJzdF9yQ0MrMmRqcmZaTnBNVEg3QnNwVCIsIm5pZHMiOiJrZGtsNmMzdTFmdzJyeDowO2o2aDJjZGt5NXprN2M2OjA7ajV6cDhlc2VjbTMxcnI6MDtpeXdxdzY2cm5iNGhzOjA7ajlqMHVkcnhqanA3NTg6MDtqY2NxM2QzOWRremV1OjA7amM0ZWQyczhjM3YzZnU6MDtqYzhucDEzMDdtMzRoYTowO2ppYTBtcG5waWxsNTl5OjA7amhhZGx0dXI1OXd0dTowO2h5cTBicjF1M2t4N2RnOjA7amtzMzNkNjgzOWk1Y286MDtqbDJubDE3ZzNybDdwZjowO2psMnc4dmg0bGEzMTA1OjA7anFmZWJsazdlcWgxMms6MDtqcXR5cjNxNHJ5bzR6MzowO2p6M25ydWQ1YmltNXRkOjA7anpkYzg0MGh3bWQ3ZGM6MDtrNW5odHdscWJ0YTYybDowO2s1bmRvNzAyOTRxNWZtOjA7azVqMmswZm56ajkxdmg6MDtrNThzYWd6NW12bzUxNDowO2s3dmgydDlyZWNkNXQ4OjA7a2Uzc2pzcGRtbnQ2NXI6MDtrZWVqN29xM2FvNDdhcDowOyIsInRhZyI6IiIsInVzZXIiOiJqNmxldzU2MDRoejJsaSIsImVtYWlsIjoia3J0aGFrZXIxMjI0QGJlcmtlbGV5LmVkdSJ9.zYROvXSmhR%2BIKyO1tnRUjVMdDxsf2HJxIAl2VzArMpM%3D',
}

params_remove = (
    ('method', 'network.drop'),
    ('aid', 'kf0bgbgfqblr'),
)

def enroll(course_id):
	data = {
		"method":"network.join",
		"params":{
			"email":"krthaker1224@berkeley.edu",
			"nids":[course_id],
			"nids_ta":[],
			"nids_prof":[],
			"codes":{},
			"uid":"j6lew5604hz2li"
		}
	}
	r = requests.post('https://piazza.com/logic/api', headers=headers_enroll, params=params_enroll, cookies=cookies_enroll, data=json.dumps(data))
	if r.ok:
		return r
	else:
		print(r)

def remove(course_id):
	data = {
		"method":"network.drop",
		"params":{
			"nid":course_id
		}
	}
	return requests.post('https://piazza.com/logic/api', headers=headers_remove, params=params_remove, cookies=cookies_remove, data=json.dumps(data))
	if r.ok:
		return
	else:
		print(r)


# info = requests.get('https://piazza.com/class/ke3sjspdmnt65r', auth=('krthaker1224@berkeley.edu', 'Bajrangbali@24'))
# print(info.text)

# with open('course_info.json', 'r+') as f:
# 	data = json.load(f)
# 	for e in data['result']['networks']:
# 		print(f"Folders for {e['my_name']}: {', '.join(e['folders'])}")

import requests

cookies_class = {
    'session_id': '6cov6wa7Ac7fNjQHVTRNC32a',
    'last_piaz_user': 'j6lew5604hz2li',
    '_ga': 'GA1.2.1667166114.1598380832',
    '_gid': 'GA1.2.1090627222.1599809848',
    'AWSELB': '732545B312943CE3A5A159C88B79D008FE4AE6530D4961FC799B730990AAC6BF6A7C51E1A6F8B52B8DC7FE8DDDE410C9041903251F5D23AC87D809FE3C293EA15EEB6C40E7',
    'AWSELBCORS': '732545B312943CE3A5A159C88B79D008FE4AE6530D4961FC799B730990AAC6BF6A7C51E1A6F8B52B8DC7FE8DDDE410C9041903251F5D23AC87D809FE3C293EA15EEB6C40E7',
    'piazza_session': '1.eyJleHBpcmVzIjoxNjAxMTAyOTQxLCJwZXJtIjoiMCIsImxvZ2dpbmdfaW4iOnRydWUsImNyZWF0ZWRfYXQiOjE1OTk4OTMzNDEsIndoZW4iOjE1OTk4OTMzMzAsImhvbWUiOiIvIiwicmVtZW1iZXIiOiJvbiIsInNlc3Npb25fdG9rZW4iOiJzdF9yQ0MrMmRqcmZaTnBNVEg3QnNwVCIsIm5pZHMiOiJrZTNzanNwZG1udDY1cjowO2o2aDJjZGt5NXprN2M2OjA7ajV6cDhlc2VjbTMxcnI6MDtpeXdxdzY2cm5iNGhzOjA7ajlqMHVkcnhqanA3NTg6MDtqY2NxM2QzOWRremV1OjA7amM0ZWQyczhjM3YzZnU6MDtqYzhucDEzMDdtMzRoYTowO2ppYTBtcG5waWxsNTl5OjA7amhhZGx0dXI1OXd0dTowO2h5cTBicjF1M2t4N2RnOjA7amtzMzNkNjgzOWk1Y286MDtqbDJubDE3ZzNybDdwZjowO2psMnc4dmg0bGEzMTA1OjA7anFmZWJsazdlcWgxMms6MDtqcXR5cjNxNHJ5bzR6MzowO2p6M25ydWQ1YmltNXRkOjA7anpkYzg0MGh3bWQ3ZGM6MDtrNW5odHdscWJ0YTYybDowO2s1bmRvNzAyOTRxNWZtOjA7azVqMmswZm56ajkxdmg6MDtrNThzYWd6NW12bzUxNDowO2s3dmgydDlyZWNkNXQ4OjA7a2VlajdvcTNhbzQ3YXA6MDsiLCJ0YWciOiIiLCJ1c2VyIjoiajZsZXc1NjA0aHoybGkiLCJlbWFpbCI6ImtydGhha2VyMTIyNEBiZXJrZWxleS5lZHUifQ%3D%3D.EBM%2FSjh58VWZctWASKtnqDMf1tAfM4EsaARUSfzfqbA%3D',
}

def get_data(course_id):
	headers_class = {
	    'Connection': 'keep-alive',
	    'Cache-Control': 'max-age=0',
	    'DNT': '1',
	    'Upgrade-Insecure-Requests': '1',
	    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
	    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
	    'Sec-Fetch-Site': 'same-origin',
	    'Sec-Fetch-Mode': 'navigate',
	    'Sec-Fetch-User': '?1',
	    'Sec-Fetch-Dest': 'document',
	    'Referer': f'https://piazza.com/class/{course_id}',
	    'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
	}
	page = requests.get(f'https://piazza.com/class/{course_id}', headers=headers_class, cookies=cookies_class)
	cache = re.search('PA.cache\("user.status", \{\}, (.*)\)', page.text).group(1)
	cache = json.loads(cache)
	# print([e['my_name'] for e in cache['result']['networks']])
	results = cache['result']['networks']
	try:
		course_details = [e for e in results if e['id']==course_id][0]
	except:
		return {'course_id':course_id, 'course_name': "No matching class found in cache"}
	try:
		ret = {'course_name':course_details['my_name'], 'course_id':course_details['id'], 'course_folders':course_details['folders']}
		print(ret)
		return ret
	except:
		print(f"Error for {course_id}")
		return {'course_id':course_id, 'course_name': "ERROR"}

info = {'result':[]}

temp_list=[{'id':'kcz7n0fk1ps4yv'}]
with open('berkeley_classes.json', 'r+') as f:
	data = json.load(f)
	for e in data['result']:
		course_id = e['id']
		enroll(course_id)
		# break
		course_info = get_data(course_id)
		# print(course_info)
		info['result'].append(course_info)
		remove(course_id)

with open('course_folders.json', 'r+') as f:
	f.seek(0)
	f.write(json.dumps(info, indent=4))
	f.truncate()

# with open('berkeley_classes.json', 'r+') as f:
# 	data = json.load(f)

# 	data['result'] = [{'id':e['terms']['Fall 2020']['id'], 'prof':e['terms']['Fall 2020']['prof'], 'course_num':e['cn'], 'course_name':e['n']} for e in data['result']]

# 	f.seek(0)
# 	f.write(json.dumps(data, indent=4))
# 	f.truncate()
