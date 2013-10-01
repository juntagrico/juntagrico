ortoloco.ch
===================
###die regionale gartenkooperative


We implement a "specific" web solution to organize all the work on a farm as a group of about ~400 persons.

###Setting up locally:
    sudo apt-get install virtualenv
    virtualenv --distribute venv
    source ./venv/bin/activate
    pip install -r requirements.txt
    add a file called settings_local.py to the root, change all settings as needed

###Create DB from scratch:
    in ortoloco/settings.py, comment out all non-django apps (loco_app, south, photologue)
    ./manage.py syncdb
    reactivate apps
    ./manage.py syncdb
    ./manage.py migrate

###Create new migration:
    ./manage.py schemamigration loco_app --auto
    ./manage.py migrate loco_app

###Test server:
    - ./manage.py runserver
    - will be on localhost at port 8000



