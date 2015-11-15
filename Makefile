# Abused Makefile to gather repetitive commands used for dev.
# It is also intended to be an (executable) documentation of which
# commands are used to start the dev environment.

DB_SQLITE_FILENAME=db.sqlite
DB_SQLITE_FILE_PRESENT=$(shell [ -f $(DB_SQLITE_FILENAME) ] && echo ok || echo missing )


run: openurl runserver

runserver: checkvenv checkdbfile
ifdef C9_USER
	./manage.py runserver 0.0.0.0:8080
else
	./manage.py runserver
endif

openurl: checkvenv checkdbfile
ifndef C9_USER
	(sleep 1; open http://localhost:8000)&
endif

createdb: checkvenv
	$(info At the bottom of file 'settings.py', comment out all non-django apps)
	$(info i.e. 'my_ortoloco', 'static_ortoloco', 'photologue' and 'south'.)
	$(shell read -p "Press any key to continue... " -n1 -s )
	$(info )
	$(info Now excute: ./manage.py syncdb)
	$(shell read -p "Press any key to continue... " -n1 -s )
	$(info )
	$(info Now reactivate the outcommented apps above.)
	$(shell read -p "Press any key to continue... " -n1 -s )
	$(info )
	$(info Now excute: ./manage.py syncdb)
	$(shell read -p "Press any key to continue... " -n1 -s )
	$(info )
	$(info Now excute: ./manage.py migrate)
	$(shell read -p "Press any key to continue... " -n1 -s )
	$(info )
	cp $(DB_SQLITE_FILENAME) $(DB_SQLITE_FILENAME)_clean.bak

restorecleandb: backuprejecteddb
	cp $(DB_SQLITE_FILENAME)_clean.bak $(DB_SQLITE_FILENAME)

restoredb: backuprejecteddb
	cp $(shell ls -1t $(DB_SQLITE_FILENAME)_*snapshot.bak | head -1) $(DB_SQLITE_FILENAME)

backuprejecteddb:
	@ [ -f $(DB_SQLITE_FILENAME) ] && cp $(DB_SQLITE_FILENAME) $(DB_SQLITE_FILENAME)_$(shell date +"%Y%m%d%H%M%S")_rejected.bak || :

savedb: checkdbfile
	cp $(DB_SQLITE_FILENAME) $(DB_SQLITE_FILENAME)_$(shell date +"%Y%m%d%H%M%S")_snapshot.bak

listdbs:
	ls -lG $(DB_SQLITE_FILENAME)*

migratedb: checkvenv
	./manage.py schemamigration my_ortoloco --auto || true
	./manage.py migrate my_ortoloco || true
	./manage.py schemamigration static_ortoloco --auto || true
	./manage.py migrate static_ortoloco || true

HEROKU_APP ?= ortoloco
HEROKU_LAST_BACKUP_ID = $(shell heroku pg:backups --app $(HEROKU_APP) | grep Completed | head -1 | sed "s/\(\S\S*\)\s.*/\1/")
HEROKU_LAST_BACKUP_PUBLIC_URL = $(shell heroku pg:backups public-url --app $(HEROKU_APP) | cat)
heroku_download_last_db_backup:
	$(info Downloading last backup from heroku app '$(HEROKU_APP)'...)
	curl '$(HEROKU_LAST_BACKUP_PUBLIC_URL)' --create-dirs -o git-untracked/.heroku_db_backups/$(HEROKU_APP)/$(shell date +"%Y%m%d%H%M%S")_$(HEROKU_LAST_BACKUP_ID).bak

HEROKU_SOURCE_APP ?= ortoloco
HEROKU_TARGET_APP = ortoloco-dev
heroku_refresh_dev_db:
	$(info Copying last backup from heroku app '$(HEROKU_SOURCE_APP)' into app '$(HEROKU_TARGET_APP)'...)
	heroku pg:backups restore '$(shell heroku pg:backups public-url --app $(HEROKU_SOURCE_APP))' DATABASE_URL --app $(HEROKU_TARGET_APP

checkdbfile:
ifneq ("$(DB_SQLITE_FILE_PRESENT)","ok")
	$(error DB file $(DB_SQLITE_FILENAME) missing...)
endif

checkvenv: checkdbenvvariables
ifndef VIRTUAL_ENV
	$(warning venv is not yet set up correctly for this shell)
	$(error Run following command to enable it: source venv/bin/activate)
endif

checkdbenvvariables:
ifndef ORTOLOCO_DATABASE_ENGINE
	$(info FIX => export ORTOLOCO_DATABASE_ENGINE=django.db.backends.sqlite3)
	$(error ORTOLOCO_DATABASE_ENGINE is not defined.)
endif
ifndef ORTOLOCO_DATABASE_NAME
	$(info FIX => export ORTOLOCO_DATABASE_NAME=db.sqlite)
	$(error ORTOLOCO_DATABASE_NAME is not defined.)
endif
