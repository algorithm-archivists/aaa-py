default: local

install:
	cd build && pipenv install

build: build/main.py
	cd build && pipenv run python3 main.py

build_local: build/main.py
	cd build && pipenv run python3 main.py --local

serve:
	cd build/website && pipenv run python3 -m http.server 8080

main: | install build serve

local: | build_local serve

.PHONY: build build_local install local main serve
