import os

OWNER_NAME = ''  # github organization name
REPO_NAME = ''  # github repository name

GITHUB_ACCESS_TOKEN = ''  # github token to access api

SLACKBOT_TOKEN = ''  # slack token to send messages


for key, value in globals().copy().items():
    if key.isupper() and key in os.environ:
        globals()[key] = os.environ[key]
