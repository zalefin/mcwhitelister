#!/usr/bin/env python3
#
# Run a website to generate token links to give to friends, add to minecraft whitelist
#
from flask import Flask, render_template, request
import requests
from argparse import ArgumentParser
from random import randint
import json
import os

app = Flask(__name__)

try:
    SERVER_NAME = os.environ["SERVER_NAME"]
except:
    SERVER_NAME = ""

try:
    TOKENS_PATH = os.environ["TOKENS_PATH"]
except:
    TOKENS_PATH = "./tokens.json"

try:
    WHITELIST_PATH = os.environ["WHITELIST_PATH"]
except:
    WHITELIST_PATH = "./whitelist.json"
PLAYER_API = "https://playerdb.co/api/player/minecraft/{username}"

# Debug mode
HOST = "127.0.0.1"
PORT = 8000


def get_uuid(username):
    response = requests.get(PLAYER_API.format(username=username)).json()
    if response["success"]:
        return response["data"]["player"]["id"]
    else:
        return None


def get_tokens():
    with open(TOKENS_PATH, "r") as f:
        tokens = json.loads(f.read())
    return tokens


def make_token():
    token = str(randint(111111, 999999))
    tokens = get_tokens()
    tokens.append(token)
    with open(TOKENS_PATH, "w") as f:
        f.write(json.dumps(tokens))
    return token


@app.route("/whitelist")
def home():
    token = request.args.get("token")
    return render_template("main.html", token=token, server_name=SERVER_NAME)


@app.route("/submit", methods=["POST"])
def submit():
    if request.method == "POST":
        token = request.form["token"]
        tokens = get_tokens()
        if token in tokens:
            username = request.form["username"]
            uuid = get_uuid(username)
            if not uuid:
                return render_template("error.html", error="Not a valid username!")

            if len(username) < 30:
                # remove token from file
                tokens.remove(token)
                with open(TOKENS_PATH, "w") as f:
                    f.write(json.dumps(tokens))

                # update whitelist
                with open(WHITELIST_PATH, "r") as f:
                    whitelist = json.loads(f.read())
                entry = {"uuid": uuid, "name": username}
                if not entry in whitelist:
                    whitelist.append(entry)
                with open(WHITELIST_PATH, "w") as f:
                    f.write(json.dumps(whitelist))

                return render_template("success.html", username=username)

            else:
                return render_template(
                    "error.html", error="Username must be < 30 chars"
                )
        else:
            return render_template("error.html", error="Invalid token")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--token", "-t", action="store_true")
    args = parser.parse_args()

    if args.token:
        token = make_token()
        print(f"https://{HOST}/whitelist?token={token}")
    else:
        app.run(debug=True, host=HOST, port=PORT)
