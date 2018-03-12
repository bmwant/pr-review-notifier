import os


DATABASE_URL = ''  # URL to your postgres database
BASE_URL = ''  # hostname where application is deployed

OWNER_NAME = ''  # github organization name
REPO_NAME = ''  # github repository name

GITHUB_API_BASE = 'https://api.github.com/'
GITHUB_ACCESS_TOKEN = ''  # github token to access api

DEFAULT_LABEL_NAME = 'Needs review'

SLACKBOT_TOKEN = ''  # slack token to send messages
DEFAULT_SLACK_CHANNEL = '#notifications'
DEFAULT_SLACK_BOT_NAME = 'gitbot'
DEFAULT_SLACK_ICON = ':baby_chick:'

REQUIRED_REVIEWERS = 2  # amount of required reviews for one pull request

HEALTHCHECK_ENDPOINT = ''
HEALTHCHECK_INTERVAL = 30 * 60

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
