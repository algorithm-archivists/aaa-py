default: main

# This file will expand to cover more cases, like initial install of pipenv and initial pip packages.

install:
	pipenv install

main: build/main.py
	$(MAKE) install
	cd build && pipenv run python3 main.py && cd ../website && python3 -m http.server 8080
