import os

OWNER_NAME = ''  # github organization name
REPO_NAME = ''  # github repository name

GITHUB_ACCESS_TOKEN = ''  # github token to access api

SLACKBOT_TOKEN = ''  # slack token to send messages


# Override values from config_local.py
try:
    import config_local
    for key, value in config_local.__dict__.items():
        if key.isupper() and key in globals():
            globals()[key] = value
except ImportError:
    pass

# Override values from environment
for key, value in globals().copy().items():
    if key.isupper() and key in os.environ:
        globals()[key] = os.environ[key]
