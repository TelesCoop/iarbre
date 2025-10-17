#!/bin/bash
include .env

FRONT_CMD = cd front/ && . ~/.nvm/nvm.sh && nvm use
BACK_CMD = cd back/ && pew in ${PEW_ENV} python manage.py
# Install front
install_front:
	${FRONT_CMD} && npm install

# Run dev server
run_front:
	${FRONT_CMD} && npm run dev

# Run dev server
build_front:
	${FRONT_CMD} && npm run build

# Run dev server
lint_front:
	${FRONT_CMD} && npm run lint

# Tests unit
tests_unit:
	${FRONT_CMD} && npm run test

# Tests cypress dev
tests_cypress:
	${FRONT_CMD} && npm run test:cypress

# Test cypress dev
tests_cypress_dev:
	${FRONT_CMD} && npm run test:cypress:dev

# Run backend server
run_back:
	${BACK_CMD} runserver

# Migrate db
back_cmd:
	${BACK_CMD} ${cmd}

# Migrate db
back_migrate:
	${BACK_CMD} migrate ${cmd}

# Make migrations db
back_makemigration:
	${BACK_CMD} makemigrations

# Recover db and media without deleting some models
safe_recovery:
	${BACK_CMD} safe_recovery
# Recover db and media
back_recover_db_and_media:
	${BACK_CMD} backup_db recover_db_and_media
# Shell in back
back_shell:
	${BACK_CMD} shell
