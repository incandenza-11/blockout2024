## start the script
start:
	docker-compose run -it --build blockout

## clear instagram session
ig/clear-session:
	rm resources/cache/instagram/*-session.json