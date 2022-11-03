### Deployment to Heroku

Initialize remote for the first time

```bash
$ heroku login
$ heroku git:remote -a pr-review-notifier
$ git remote -v | grep heroku
```

Set all the required environment variables

```bash
$ heroku config:set BASE_URL='https://<your-app-name>.herokuapp.com/'
$ heroku config:set GITHUB_CLIENT_ID='<your-client-id>'
$ heroku config:set GITHUB_CLIENT_SECRET='<your-client-secret>'
```

Do not forget to set env variables first in `.env` file or push them manually 
([link](https://devcenter.heroku.com/articles/config-vars#setting-up-config-vars-for-a-deployed-application)).

Trigger deployment with 

```bash
$ poetry export -f requirements.txt
$ make deploy-heroku
```

### Customization

Override config variables for Heroku, e.g. setting custom bot icon

```bash
$ heroku config:set DEFAULT_SLACK_ICON=':octocat:'
```

### Troubleshooting

Useful commands to figure out what's going wrong

```bash
$ heroku logs  # show process output
$ heroku restart  # restart application on remote
$ heroku run bash  # login to the remote shell
$ heroku buildpacks:remove heroku/nodejs  # remove unused buildpack
```