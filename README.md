ortoloco.ch
===========

**die regionale gartenkooperative**

We implement a "specific" web solution to organize all the work on a
farm as a group of about ~400 persons.

# Setting up locally

Following instructions work for MacOS.

## Installing requirements

    pip install virtualenv
    virtualenv --distribute venv
    source ./venv/bin/activate
    pip install --upgrade -r requirements.txt

**NOTE:** All requirements are not _easily installable_ on Mac OS X. If you encounter some issues (i.e. `EnvironmentError: mysql_config not found` or `pg_config executable not found`) you might remove following packages from the requirements:
  - MySQL-python==1.2.5
  - django-toolbelt==0.0.1
  - psycopg2==2.5.1


## Create DB from scratch

In [ortoloco/settings.py](https://github.com/ortoloco/ortoloco/blob/5b8bf329e6d01fc6b6f4215a514c8fa456e09cf7/ortoloco/settings.py#L166-L169), comment out all non-django apps (loco_app, south, photologue). Then
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
