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

``` bash
    export ORTOLOCO_DATABASE_ENGINE=django.db.backends.sqlite3
    export ORTOLOCO_DATABASE_NAME=db.sqlite
    export ORTOLOCO_EMAIL_HOST=smtp.gmail.com
    export ORTOLOCO_EMAIL_PASSWORD=YOUR_GMAIL_APP_PASSWORD
    export ORTOLOCO_EMAIL_USER=YOUR_EMAIL@gmail.com
    export ORTOLOCO_EMAIL_WHITELISTED_1=A_SECOND_WHITELISTED_EMAIL@gmail.com # optional
```

### Email troubleshooting

In case the `gmail` credentials refuse to work, it might be that Google
is blocking the logging because is it comming from an unknown location.
This can easily be the case if using e.g. [`c9.io`](https://c9.io/).
Try the solutions listed in this [Gmail Help](https://support.google.com/mail/answer/78754)
document. The first three of them are listed here for reference:

> - If you've turned on 2-Step Verification for your account, you might
  need to enter an App password.
> - Sign in to your account from the web version of Gmail at
  <https://mail.google.com>. Afterwards try accessing your messages in
  your mail app again.
> - If you're still having problems, visit
  <http://www.google.com/accounts/DisplayUnlockCaptcha> and sign in with
  your Gmail username and password. If necessary, enter the letters in
  the distorted picture.



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

Here you will be asked to create a `superuser` for the local dev app.
Reply `yes` and create a test superuser named e.g. `admin` with the
(indeed very secure) password `admin`. The output should look similar
to the following:

```
(...)

Creating tables ...
Creating table django_cron_job
Creating table django_cron_cron
Creating table auth_permission
Creating table auth_group_permissions
Creating table auth_group
Creating table auth_user_groups
Creating table auth_user_user_permissions
Creating table auth_user
Creating table django_content_type
Creating table django_session
Creating table django_site
Creating table django_admin_log

You just installed Django's auth system, which means you don't have any superus
ers defined.
Would you like to create one now? (yes/no): yes
Username (leave blank to use 'ubuntu'): admin
Email address: admin@example.org
Password:
Password (again):
Superuser created successfully.
Installing custom SQL ...
Installing indexes ...
Installed 0 object(s) from 0 fixture(s)

```

Reactivate the outcommented apps above and run following commands:

    ./manage.py syncdb
    ./manage.py migrate

You might be guided through the steps above with `make createdb`.

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

#### Between Heroku apps

    SOURCE_APP=ortoloco
    TARGET_APP=ortoloco-dev
    heroku pg:backups restore $(heroku pg:backups public-url --app $SOURCE_APP) DATABASE_URL --app $TARGET_APP

See: [Importing and Exporting Heroku Postgres Databases with PG Backups](https://devcenter.heroku.com/articles/heroku-postgres-import-export)

### How to deploy to ortoloco-dev.herokuapp.com

Obviously, you need the rights to do this, then:

    heroku git:remote -a ortoloco-dev -r heroku-dev
    git push heroku-dev master

On live you do this:

    heroku git:remote -a ortoloco -r heroku-live
    git push heroku-live live
