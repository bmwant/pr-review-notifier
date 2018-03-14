deploy:
	git push heroku master

runpg:
	docker rm local-postgres | true
	docker run --name local-postgres -v pgdata:/var/lib/postgresql/data -d postgres
