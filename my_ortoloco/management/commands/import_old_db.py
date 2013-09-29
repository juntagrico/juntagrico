import MySQLdb

from django.core.management.base import BaseCommand, CommandError

from my_ortoloco.models import *

#from polls.models import Poll

class Command(BaseCommand):
    def connect(self, user, passwd):
        db = MySQLdb.connect(host="my2.ortoloco.ch",
                             user=user,
                             passwd=passwd,
                             db="my2ortoloco")

        self.cur = db.cursor()

    def query(self, querystring):
        self.cur.execute(querystring)
        for row in self.cur.fetchall():
            yield row


    # entry point used by manage.py
    def handle(self, *args, **options):
        self.connect(*args)

        new_users = []
        for row in self.query("SELECT * FROM usr"):
            email=row[0]

            # convert from latin-1 encoded string to unicode object, which is 
            # automagically handled by Django
            email = email.decode("latin-1")

            user = User(username=email)
            new_users.append(user)


        # get existing users from db
        old_users = set(User.objects.all())

        # bulk_create groups everything into a single query. However, Post-create events won't be sent
        # so Loco instances have to be created manually.
        User.objects.bulk_create(new_users)

        # get fresh user objects back from db, now with primary keys etc.
        new_users = set(User.objects.all()) - old_users

        # create loco for each new user
        Loco.objects.bulk_create(Loco(user=user) for user in new_users)

