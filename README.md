
setting up:
    sudo apt-get install virtualenv
    virtualenv --distribute venv
    source ./venv/bin/activate
    pip install -r requirements.txt


create DB from scratch:
    in ortoloco/settings.py, comment out all non-django apps (loco_app, south, photologue)
    ./manage.py syncdb
    reactivate apps
    ./manage.py syncdb
    ./manage.py migrate loco_app
    ./manage.py migrate photologue

create new migration:
    ./manage.py schemamigration loco_app --auto
    ./manage.py migrate loco_app

test server:
    - ./manage.py runserver
    - will be on localhost at port 8000



