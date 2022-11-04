.PHONY: install
install:
	@poetry install

deploy-heroku:
	git push heroku master
