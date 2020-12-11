#!/usr/bin/python3

import requests
import json
import os
import datetime
import time

repo = os.getenv('GITHUB_REPOSITORY')
api_url = "https://api.github.com/repos/" + repo + "/actions/workflows/"
token = os.getenv('GITHUB_TOKEN')
current_branch = os.getenv('GITHUB_HEAD_REF')
current_run_id = os.getenv('GITHUB_RUN_ID')
workflow_file_name = os.getenv('WORKFLOW_FILE_NAME')
request_headers = {"Authorization": "token " + token}
workflow_runs = []
timeout_seconds = os.getenv('TIMEOUT_SECONDS', default=120)
sleep_seconds = os.getenv('SLEEP_SECONDS', default=10)

# Get ID of current workflow
request_url = api_url + workflow_file_name
r = requests.get(url=request_url, headers=request_headers)
workflow_id = str(json.loads(r.content.decode())['id'])

# Get list of workflow runs, where:
# - branch is GITHUB_HEAD_REF
# - event is 'pull_request'
# - status is 'queued' or 'in_progress'
for workflow_status in ['in_progress', 'queued']:
    request_url = api_url + workflow_id + "/runs"
    request_params = {'event': 'pull_request', 'branch': current_branch, 'status': workflow_status}
    r = requests.get(url=request_url, headers=request_headers, params=request_params)
    workflow_runs += json.loads(r.content.decode())['workflow_runs']

# Cancel all workflow runs, except current run, and wait till their status is 'completed'
for w in workflow_runs:
    if not str(w['id']) == current_run_id:
        print('Cancelling workflow: id={}, run_number={}, status={}'.format(w['id'], w['run_number'], w['status']))
        r = requests.post(url=w['cancel_url'], headers=request_headers)
        print('Waiting for the workflow to be cancelled...')
        current_time = datetime.datetime.now()
        finish_time = current_time + datetime.timedelta(seconds=timeout_seconds)
        while current_time < finish_time:
            status = json.loads(requests.get(url=w['url'], headers=request_headers).content.decode())['status']
            if status == 'completed':
                break
            time.sleep(sleep_seconds)
            current_time = datetime.datetime.now()
        print('Done')
