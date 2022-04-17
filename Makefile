build:
	docker-compose down -v
	docker-compose build
	docker-compose up -d

logs:
	docker-compose logs -f back

_shell:
	docker-compose exec back ./manage.py shell

test:
	docker-compose exec back sh ../test.sh
