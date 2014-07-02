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
    pip install -r requirements.txt

## Create DB from scratch

In [ortoloco/settings.py](https://github.com/ortoloco/ortoloco/blob/5b8bf329e6d01fc6b6f4215a514c8fa456e09cf7/ortoloco/settings.py#L166-L169), comment out all non-django apps (loco_app, south, photologue).

    ./manage.py syncdb

Then, reactivate the outcommented apps above.

    ./manage.py syncdb
    ./manage.py migrate

### Create new migration

When the database structure changes, you must perform a new migration:

    ./manage.py schemamigration loco_app --auto
    ./manage.py migrate loco_app

## Test server

Run following command to launch a server on <`http://localhost:8000`>:

    ./manage.py runserver

### Create loco for admin user

The first time you try to login with the initial admin user you will
encouter an error like `User has no Loco`. To create a `Loco` for this
user, you have to activate a secret :) URL in [`url.py`](https://github.com/ortoloco/ortoloco/blob/5b8bf329e6d01fc6b6f4215a514c8fa456e09cf7/ortoloco/urls.py#L58) and call it from the browser:

- <`http://localhost:8000/my/createlocoforsuperuserifnotexist`>

Afterwards, you might have to logout with following URL:

- <`http://localhost:8000/logout`>
