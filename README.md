ortoloco.ch
===========

[![Build Status](https://travis-ci.org/ortoloco/ortoloco.svg?branch=master)](https://travis-ci.org/ortoloco/ortoloco)

**die regionale gartenkooperative**

We implement a "specific" web solution to organize all the work on a
farm as a group of about ~400 persons.

# Setting up locally

Following instructions work for MacOS.

## Set your environment variables
This should do it for your local setup:

    export ORTOLOCO_DATABASE_ENGINE=django.db.backends.sqlite3
    export ORTOLOCO_DATABASE_NAME=db.sqlite
    export ORTOLOCO_EMAIL_HOST=smtp.gmail.com
    export ORTOLOCO_EMAIL_PASSWORD=<your-gmail-app-password>
    export ORTOLOCO_EMAIL_USER=<you>@gmail.com

## Installing requirements

### Clone repository on you machine and enter the directory

    cd ortoloco
    
### Now start installing

    sudo easy_install pip
    sudo pip install virtualenv
    virtualenv --distribute venv
    source ./venv/bin/activate
    pip install --upgrade -r requirements.txt

**NOTE:** All requirements are not _easily installable_ on Mac OS X. If you encounter some issues (i.e. `EnvironmentError: mysql_config not found` or `pg_config executable not found`) you might run instead:

    pip install --upgrade -r requirements-mac.txt

wich removes following packages from the requirements:

    MySQL-python==1.2.5
    django-toolbelt==0.0.1
    psycopg2==2.5.1

**NOTE:** You might be able to install "brew install mysql" and "brew install postgresql" and "brew install pg" instead (before)

## Create DB from scratch

In [ortoloco/settings.py](https://github.com/ortoloco/ortoloco/blob/5b8bf329e6d01fc6b6f4215a514c8fa456e09cf7/ortoloco/settings.py#L166-L169), comment out all non-django apps (loco_app ,my_ortoloco,static_ortoloco, south, photologue). Then
run following command:

    ./manage.py syncdb

Reactivate the outcommented apps above and run following commands:

    ./manage.py syncdb
    ./manage.py migrate

You might be guided through these steps with `make createdb`.

### Backup and restore local dev database

With `make savedb` you can easily make a snapshot of the current local
database file (if using `SQLite`), and restore it (i.e. the last db
snapshot file) with `make restoredb`.

You might want to look at the [`Makefile`](https://github.com/ortoloco/ortoloco/blob/master/Makefile) for more details.

### Create new migration

When the database structure changes, you must perform a new migration:

    ./manage.py schemamigration loco_app --auto
    ./manage.py migrate loco_app

You might be guided through these steps with `make migratedb`.

## Test server

Run following command to launch a server on <http://localhost:8000>:

    ./manage.py runserver

You might run this with `make`, which will additionally open the URL
on your browser.

### Create admin user

Use following command to create a super user, if not yet available:

    manage.py createsuperuser


### Create loco for admin user

The first time you try to login with the initial admin user you will
encouter an error like `User has no Loco`. To create a `Loco` for this
user, you have to activate a secret :smile: URL in [`url.py`](https://github.com/ortoloco/ortoloco/blob/5b8bf329e6d01fc6b6f4215a514c8fa456e09cf7/ortoloco/urls.py#L58) and call it from the browser:

- <http://localhost:8000/my/createlocoforsuperuserifnotexist>

Afterwards, you might have to logout with following URL:

- <http://localhost:8000/logout>

### Change password for super user ('admin' is the username)

    ./manage.py changepassword admin


### How to migrate from mysql to postgres-sql
First read this:
https://github.com/lanyrd/mysql-postgresql-converter

Then import the data into the heroku-db (find the values here: https://postgres.heroku.com/databases/ortoloco-database)
psql -U <username> -d <database> -h <host-of-db-server> -f path/to/postgres.sql

### How to move the live-data to dev
