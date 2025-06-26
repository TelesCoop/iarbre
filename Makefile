#!/bin/bash
include .env

# Install front
install_front:
	cd front/ && . ~/.nvm/nvm.sh && nvm use && npm install

# Run dev server
run_front:
	cd front/ && . ~/.nvm/nvm.sh && nvm use && npm run dev

# Run dev server
build_front:
	cd front/ && . ~/.nvm/nvm.sh && nvm use && npm run build

# Run backend server
run_back:
	cd back/ && pew in ${PEW_ENV} python manage.py runserver

# Migrate db
back_migrate:
	cd back/ && pew in ${PEW_ENV} python manage.py migrate

# Recover db and media without deleting some models 
safe_recovery:
	cd back/ && pew in ${PEW_ENV} python manage.py safe_recovery

# Recover db and media
back_recover_db_and_media:
	cd back/ && pew in ${PEW_ENV} python manage.py backup_db recover_db_and_media

# Shell in back
back_shell:
	cd back/ && pew in ${PEW_ENV} python manage.py shell
# Run dev server
lint_front:
	cd front/ && . ~/.nvm/nvm.sh && nvm use && npm run lint

# Tests unit
tests_unit:
	cd front/ && . ~/.nvm/nvm.sh && nvm use && npm run test

# Tests cypress dev
tests_cypress:
	cd front/ && . ~/.nvm/nvm.sh && nvm use && npm run test:cypress

# Test cypress dev
tests_cypress_dev:
	cd front/ && . ~/.nvm/nvm.sh && nvm use && npm run test:cypress:dev
