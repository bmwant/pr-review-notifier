# PR review notifier

Elevate github webhooks and integrations with popular messengers to notify 
developers about PRs waiting for the review.

### Deploy

Deploy is done with a help of Heroku.

Do not forget to set env variables first in `.env` file or push them manually ([link](https://devcenter.heroku.com/articles/config-vars#setting-up-config-vars-for-a-deployed-application)).

Override config variables for Heroku, e.g. setting custom bot icon
```
$ heroku config:set DEFAULT_SLACK_ICON = ':octocat:'
```
