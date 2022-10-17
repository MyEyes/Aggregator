#!/bin/sh
set -x
TOKEN=$(curl -X POST -u 'firzen:firzen' http://127.0.0.1:5000/api/auth/tokens | grep token | sed s/\"token\":// | sed s/\"//g | sed s/\ //g)
curl -X POST -H "Authorization:Bearer $TOKEN" \
-d '{"scan_hash":"aaaa", "scan_soft_hash":"bbbb", "arguments": "test arguments", "tool_name":"test tool"}' \
-H 'Content-Type: application/json' http://127.0.0.1:5000/api/scan/start

curl -X POST -H "Authorization:Bearer $TOKEN" \
-d '{"scan_hash":"aaaa"}' \
-H 'Content-Type: application/json' http://127.0.0.1:5000/api/scan/stop