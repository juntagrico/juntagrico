# Abused Makefile to gather repetitive commands used for dev.
# It is also intended to be an (executable) documentation of which
# commands are used to start the dev environment.

DB_SQLITE_FILENAME=db.sqlite
DB_SQLITE_FILE_PRESENT=$(shell [ -f $(DB_SQLITE_FILENAME) ] && echo ok || echo missing )

run: openurl runserver

runserver: checkvenv checkdbfile
	./manage.py runserver

openurl: checkvenv checkdbfile
	(sleep 1; open http://localhost:8000)&

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
	./manage.py schemamigration loco_app --auto
	./manage.py migrate loco_app

checkdbfile:
ifneq ("$(DB_SQLITE_FILE_PRESENT)","ok")
	$(error DB file $(DB_SQLITE_FILENAME) missing...)
endif

checkvenv:
ifndef VIRTUAL_ENV
	$(warning venv is not yet set up correctly for this shell)
	$(error Run following command to enable it: source venv/bin/activate)
endif


# @ [ -f $(DB_SQLITE_FILENAME) ] || { echo "DB file $(DB_SQLITE_FILENAME) missing..." 1>&2; exit 1; }
