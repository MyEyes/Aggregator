#!/bin/sh
set -x
TOKEN=$(curl -X POST -u 'firzen:firzen' http://127.0.0.1:5000/api/auth/tokens | grep token | sed s/\"token\":// | sed s/\"//g | sed s/\ //g)
curl -X POST -H "Authorization:Bearer $TOKEN" \
-d '{"soft_match_hash":"aaaa", "hard_match_hash":"bbbb", "version": "1.0", "name":"test tool", "description": "Dummy Tool"}' \
-H 'Content-Type: application/json' http://127.0.0.1:5000/api/tool/register
