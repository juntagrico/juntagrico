import MySQLdb

from django.core.management.base import BaseCommand, CommandError

from my_ortoloco.models import *


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

        self.create_users()


    def create_users(self):
        """
        Import user data from old db, creating a User instance and a linked Loco instance.
        """
        assert Users.objects.all().count() == 1

        new_users = []
        query = list(self.query("SELECT * FROM usr"))
        for row in query:
            email=row[0]

            # convert from latin-1 encoded string to unicode object, which is 
            # automagically handled by Django
            email = email.decode("latin-1")

            user = User(username=email)
            new_users.append(user)


        # bulk_create groups everything into a single query. Post-create events won't be sent.
        User.objects.bulk_create(new_users)

        new_locos = []
        users = list(User.object.all())
        users = users[1:] # kick out super user
        for user, row in zip(users, query):
            loco = Loco(user=user)
            new_locos.append(loco)

        Loco.objects.bulk_create(new_locos)

