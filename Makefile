#!/bin/bash
include .env


# Run dev server
run_front:
	cd front/ && . ~/.nvm/nvm.sh && nvm use && npm run dev

# Run backend server
run_back:
	cd back/ && pew in ${PEW_ENV} python manage.py runserver

# Migrate db
back_migrate:
	cd back/ && pew in ${PEW_ENV} python manage.py migrate

# Recover db and media
back_recover_db_and_media:
	cd back/ && pew in ${PEW_ENV} python manage.py backup_db recover_db_and_media
