#! /bin/bash

set -e

wait_until_up () {
  until curl $1; do
    >&2 echo "$2 is unavailable - sleeping...."
    sleep $3
  done
  >&2 echo "$2 is up..."
}

# wait for depended service ready
wait_until_up http://store:5999 store 0.5
wait_until_up http://elasticsearch:9200 elasticsearch 1.0


>&2 echo "start run jper web server"
python3 /opt/jper/service/web.py
