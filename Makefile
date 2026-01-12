#!/bin/bash
include .env

FRONT_CMD = cd front/ && . ~/.nvm/nvm.sh && nvm use
BACK_CMD_BASE = cd back/ && pew in ${PEW_ENV}
BACK_CMD = ${BACK_CMD_BASE} python manage.py
# Install front
install_front:
	${FRONT_CMD} && npm install --ignore-scripts && npx allow-scripts

# Install back
install_back:
	${BACK_CMD_BASE} pip install -r requirements.txt

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

# Recover db and media from file specified in .db_recover_target
# Use USE_FILE=no to ignore .db_recover_target and use latest backup
# Example: make back_recover_db_and_media USE_FILE=no
back_recover_db_and_media:
	@if [ "$(USE_FILE)" = "no" ]; then \
		${BACK_CMD} backup_db recover_db_and_media; \
	elif [ -f .db_recover_target ]; then \
		${BACK_CMD} backup_db recover_db_and_media $$(cat .db_recover_target); \
	else \
		${BACK_CMD} backup_db recover_db_and_media; \
	fi

# Backup db and media
back_backup_db_and_media:
	${BACK_CMD} backup_db backup_db_and_media --zipped

# List backup db and media
back_backup_list:
	${BACK_CMD} backup_db list

# Shell in back
back_shell:
	${BACK_CMD} shell
