import requests
from requests.auth import HTTPBasicAuth
import sys


# PRE-DEFINED VAR
auth = HTTPBasicAuth(str(sys.argv[2]), str(sys.argv[3]))
redmine_url = str(sys.argv[1])
headers = {"Content-Type": "application/json"}


# PRE-DEFINED DEF
# def get_user_id():
#     r = requests.get(redmine_url + '/users/current.json', auth=auth)
#     user_id = r.json()['user']['id']
#     return user_id
#
#
# def get_spent_time_on_date(date):
#     r = requests.get(redmine_url + '/time_entries.json?from=' + date + '&to=' + date + '&user_id=' +
#                      str(get_user_id()), auth=auth)
#     spent_time = 0
#     for time_entry in r.json()['time_entries']:
#         spent_time += time_entry['hours']
#     return spent_time


# get UNCONFIRMED tasks (status_id=2) and set to CONFIRMED
response = requests.get(redmine_url + '/issues.json?assigned_to_id=me&status_id=2', auth=auth)
for issue in response.json()['issues']:
    try:
        r = requests.put(redmine_url + '/issues/' + str(issue['id']) + ".json", data='{"issue": {"status_id": 3}}',
                         auth=auth, headers=headers)
        if r.status_code == 200:
            print("Updated issue(" + str(issue['id']) + ") status from UNCONFIRMED to CONFIRMED successfully")
        else:
            print("Can not update issue(" + str(issue['id']) + ") status from UNCONFIRMED to CONFIRMED ")
    except Exception as e:
        print(e)

# log time for CONFIRMED tasks (currently only support for tasks have start_date==due_date)
response = requests.get(redmine_url + '/issues.json?assigned_to_id=me&status_id=3', auth=auth)
for issue in response.json()['issues']:
    try:
        if issue['start_date'] == issue['due_date']:
            estimated_hours = issue['estimated_hours']
            r = requests.get(redmine_url + '/time_entries.json?issue_id=' + str(issue['id']), auth=auth)
            data_time_entries = r.json()
            spent_time = 0
            for time_entry in data_time_entries['time_entries']:
                spent_time += time_entry['hours']
            if estimated_hours > spent_time:
                r_data = '{"time_entry": {"issue_id": ' + str(issue['id']) + ', "spent_on": "' + issue["due_date"] + \
                         '", "hours": ' + str(estimated_hours - spent_time) + '}}'
                r = requests.post(redmine_url + '/time_entries.json', data=r_data, auth=auth,
                                  headers=headers)
                if r.status_code == 404:
                    print("Logged time for issue(" + str(issue['id']) + ") successfully")
                else:
                    print("Can not log time for issue(" + str(issue['id']) + ") successfully")
            # get CONFIRMED tasks (status_id=3) and set to RESOLVED
            # (currently only support for tasks have start_date==due_date)
            r = requests.put(redmine_url + '/issues/' + str(issue['id']) + ".json", data='{"issue": {"status_id": 5}}',
                             auth=auth, headers=headers)
            if r.status_code == 200:
                print("Updated issue(" + str(issue['id']) + ") status from CONFIRMED to RESOLVED successfully")
            else:
                print("Can not update issue(" + str(issue['id']) + ") status from CONFIRMED to RESOLVED ")
        else:
            print("Currently not support logging time for tasks that have start_date!=due_date, "
                  "log time manually by yourself, task id: " + str(issue['id']))
    except Exception as e:
        print(e)
