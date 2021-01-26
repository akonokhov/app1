#!/bin/bash

source ${SCRIPTS_PATH}/shell.sh

curl -i -X POST \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Content-Type: application/json" \
  --data "{
    \"event_type\": \"production_deploy\",
    \"client_payload\": {
      \"triggered_by\": {
        \"github_workflow\": \"$GITHUB_WORKFLOW\",
        \"github_run_id\": \"$GITHUB_RUN_ID\",
        \"github_run_number\": \"$GITHUB_RUN_NUMBER\"
      }
    }
  }" \
  https://api.github.com/repos/${GITHUB_REPOSITORY}/dispatches
