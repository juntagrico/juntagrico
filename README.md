
setting up:
    sudo apt-get install virtualenv
    virtualenv --distribute venv
    source ./venv/bin/activate
    pip install -r requirements.txt
    ./manage.py syncdb

create new migration
    ./manage.py schemamigration loco_app --auto
    ./manage.py migrate loco_app

test server:
    - ./manage.py runserver
    - will be on localhost at port 8000



