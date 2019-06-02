# PR review notifier

Elevate github webhooks and integrations with popular messengers to notify 
developers about PRs waiting for the review.

### Getting started

Start your local PostgreSQL development database using 
[docker](https://www.docker.com/)
```
$ docker volume create pgdata
$ docker run --name local-postgres -v pgdata:/var/lib/postgresql/data \
-d postgres
$ docker run -it --rm --link local-postgres:postgres postgres \
psql -h postgres -U postgres
postgres=# CREATE DATABASE pr_review_notifier;
postgres=# \q
$ docker run -it -v $(pwd):/opt --rm --link local-postgres:postgres postgres \
psql -h postgres -U postgres -d pr_review_notifier -f /opt/init_database.sql
```

### Testing

You can simulate requests from github via this command
```
$ curl -v -H "Content-Type: application/json" -X POST \
--data @test/test_labeled.json http://localhost:8080/payload
```

for testing purposes.

### Deploy

Deploy is done with a help of Heroku.
Initialize remote for the first time
```
$ heroku run "psql \$DATABASE_URL -f init_database.sql"
$ heroku config:set BASE_URL='https://<your-app-name>.herokuapp.com/'
$ heroku config:set GITHUB_CLIENT_ID='<your-client-id>'
$ heroku config:set GITHUB_CLIENT_SECRET='<your-client-secret>'
```

Do not forget to set env variables first in `.env` file or push them manually 
([link](https://devcenter.heroku.com/articles/config-vars#setting-up-config-vars-for-a-deployed-application)).

### Customization

Override config variables for Heroku, e.g. setting custom bot icon
```
$ heroku config:set DEFAULT_SLACK_ICON=':octocat:'
```

### Troubleshooting

Useful commands to figure out what's going wrong
```
$ heroku logs  # show process output
$ heroku restart  # restart application on remote
$ heroku run bash  # login to the remote shell
$ heroku buildpacks:remove heroku/nodejs  # remove unused buildpack
```
