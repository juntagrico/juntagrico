import MySQLdb
import datetime, re

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


    def decode_row(self, row):
        return [i.decode("latin-1") if isinstance(i, basestring) else i for i in row]

    # entry point used by manage.py
    def handle(self, *args, **options):
        self.connect(*args)

        self.create_users()


    def create_users(self):
        """
        Import user data from old db, creating a User instance and a linked Loco instance.
        """
        assert User.objects.all().count() == 1

        query = list(self.query("SELECT * FROM person p "
                                "    LEFT OUTER JOIN usr u ON p.pid = u.pid "
                                "UNION ALL "
                                "SELECT * FROM person p "
                                "    RIGHT OUTER JOIN usr u ON p.pid = u.pid "
                                "WHERE p.pid is null"))

        # everything wer're throwing out here is bad data of some form...
        oldsize = len(query)
        query = [row for row in query if None not in (row[0], row[15])]
        if len(query) < oldsize:
            print "warning: some inconsistent data, ignoring..."

        new_users = []
        for row in query:
            pid, name, vorname, strasse, plz, ort, tel1, tel2, email, geburtsdatum, confirmed, timestamp, \
            uid, pwd, lvl, _ = row

            user = User(username=uid.decode("latin-1"))
            new_users.append(user)

        # bulk_create groups everything into a single query. Post-create events won't be sent.
        User.objects.bulk_create(new_users)

        new_locos = []
        users = sorted(User.objects.all(), key=lambda u: u.id)
        users = users[1:] # kick out super user

        for user, row in zip(users, query):
            pid, name, vorname, strasse, plz, ort, tel1, tel2, email, geburtsdatum, confirmed, timestamp, \
            uid, pwd, lvl, _ = self.decode_row(row)

            if not re.match(r'\d{2}\.\d{2}\.\d{4}', geburtsdatum):
                # garbage
                geburi_date = None
            else:
                # convert from 18.06.1985 to 1985-06-18
                tag, monat, jahr = [int(i) for i in geburtsdatum.split(".")]
                geburi_date = datetime.date(jahr, monat, tag)

            loco = Loco(user=user, 
                        first_name=vorname,
                        last_name=name,
                        email=email,
                        addr_street=strasse,
                        addr_zipcode=plz,
                        addr_location=ort,
                        birthday=geburi_date,
                        phone=tel1,
                        mobile_phone=tel2)

            new_locos.append(loco)

        Loco.objects.bulk_create(new_locos)

