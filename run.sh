#!/bin/sh
export TOKENS_PATH="./tokens.json"
export WHITELIST_PATH="./whitelist.json"
export SERVER_NAME="My Server"

PORT=8007

gunicorn mcwhitelister:app -b 127.0.0.1:$PORT
