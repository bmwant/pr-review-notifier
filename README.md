# PR review notifier

![octobot](icon.png)

Elevate github webhooks and integrations with popular messengers to notify developers about PRs waiting for the review.

### Testing

Create `config_local.py` with settings overrides, install dependencies and run app via

```bash
$ make install
$ poetry run python -m app
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

* [deployment to AWS Lambda](./deploy_lambda.md)
* [Deployment to Heroku](./deploy_heroku.md)
