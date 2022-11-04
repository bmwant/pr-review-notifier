.PHONY: install
install:
	@poetry install

.PHONY: run
run:
	@poetry run python -m app

.PHONY: deploy-heroku
deploy-heroku:
	git push heroku master


.PHONY: deploy-lambda
deploy-lambda:
	@poetry run zappa update dev
