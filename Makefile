.PHONY: install run build docker docker-clean

install:
	./install.sh

run:
	python3 main.py

build:
	./build.sh

docker:
	docker compose up --build

docker-clean:
	docker compose down --rmi local
