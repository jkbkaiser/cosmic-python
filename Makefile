dev: build up

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down --remove-orphans

unit-tests:
	docker-compose run --rm --no-deps --entrypoint="pytest ./tests/unit" api

integration-tests: up
	docker-compose run --rm --no-deps --entrypoint="pytest ./tests/integration" api

e2e-tests: up
	docker-compose run --rm --no-deps --entrypoint="pytest -sss ./tests/e2e" api
