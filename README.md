# PR review notifier

![octobot](icon.png)

Elevate github webhooks and integrations with popular messengers to notify 
developers about PRs waiting for the review.

### Testing

Create `config_local.py` with settings overrides, install dependencies and run 
app via

```bash
$ poetry install
$ poetry run python app.py
```

You can simulate requests from github like this

* PR was labeled

```bash
$ curl -v -H "Content-Type: application/json" \
    --data @test/payload_labeled.json http://localhost:8080/payload
```

* PR was approved

```bash
$ curl -v -H "Content-Type: application/json" \
    --data @test/payload_submitted.json http://localhost:8080/payload
```

### Deploy

Deploy is done with a help of Heroku.

Initialize remote for the first time

```bash
$ heroku config:set BASE_URL='https://<your-app-name>.herokuapp.com/'
$ heroku config:set GITHUB_CLIENT_ID='<your-client-id>'
$ heroku config:set GITHUB_CLIENT_SECRET='<your-client-secret>'
```

Do not forget to set env variables first in `.env` file or push them manually 
([link](https://devcenter.heroku.com/articles/config-vars#setting-up-config-vars-for-a-deployed-application)).

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
