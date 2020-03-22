#!/bin/bash
set -e
set -x

rm -rf /tmp/COVID-19

git clone https://github.com/CSSEGISandData/COVID-19.git /tmp/COVID-19

python3 createInitDB.py

psql --set ON_ERROR_STOP=on -q -U postgres postgres < /tmp/initdb.sql
