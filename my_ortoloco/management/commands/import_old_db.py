# -*- coding: utf-8 -*-
import datetime
import re
import itertools
from collections import defaultdict

import MySQLdb
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import timezone

from my_ortoloco.models import *


class Command(BaseCommand):
    def connect(self, user, passwd):
        db = MySQLdb.connect(host="my.ortoloco.ch",
                             user=user,
                             passwd=passwd,
                             db="myortoloco")

        self.cur = db.cursor()

    def query(self, querystring):
        self.cur.execute(querystring)
        for row in self.cur.fetchall():
            yield row

    def decode_row(self, row):
        #return [i.decode("latin-1") if isinstance(i, basestring) else i for i in row]
        return [i.decode("latin-1","ignore") if isinstance(i, basestring) else i for i in row]

    # entry point used by manage.py
    def handle(self, *args, **options):
        self.connect(*args)
        self.userids = {}

        print 'Starting migration on ', datetime.datetime.now()
        self.create_users()
        self.create_taetigkeitsbereiche()
        self.create_depots()
        self.create_taetigkeitsbereich_locos()
        self.create_jobtypes()
        self.create_jobs()
        self.create_extraabotypes()
        self.create_abos()
        self.create_abo_extra_abos()
        self.create_anteilscheine()
        print 'Finished migration on ', datetime.datetime.now()

    def create_users(self):
        """
        Import user data from old db, creating a User instance and a linked Loco instance.
        """

        print '***************************************************************'
        print 'Migrating users and locos'
        print '***************************************************************'

        assert User.objects.all().count() == 1

        query = list(self.query("SELECT * FROM person p "
                                "    LEFT OUTER JOIN usr u ON p.pid = u.pid "
                                "UNION ALL "
                                "SELECT * FROM person p "
                                "    RIGHT OUTER JOIN usr u ON p.pid = u.pid "
                                "WHERE p.pid is null "))
                                #"order by email,  confirmed desc"))


        # everything wer're throwing out here is bad data of some form...
        oldsize = len(query)
        #query = [row for row in query if None not in (row[0], row[15])]
        query = [row for row in query if None not in (row[0],)]
        if len(query) < oldsize:
            print "warning: some inconsistent data, ignoring..."


        rows_with_same_email = defaultdict(dict)

        for row in query:
            pid, name, vorname, strasse, plz, ort, tel1, tel2, email, geburtsdatum, confirmed, timestamp, \
            uid, pwd, lvl, _ = row

            rows_with_same_email[email][pid] = row

        pidswithabo = set(self.query("SELECT pid from abo"))
        #pidswithabo.update(self.query("SELECT abomit from abo"))
        new_query = []
        for email, d in rows_with_same_email.iteritems():
            overlap = pidswithabo.intersection(d.keys())
            if len(overlap) == 0:
                # take any row we want, i.e. confirmed if available, else the one with lowest pid
                chosenpid = min(d)
                for pid, row in d.items():
                    if row[10]: # confirmed
                        chosenpid = pid
                        break
                new_query.append(d[chosenpid])
            elif len(overlap) == 1:
                # take row correspinding to abo
                new_query.append(d[overlap.pop()])
            else:
                # this should never happen
                raise ValueError("error: several abos point to pids with same email %s." %email)

        query = new_query


        newid = (u"newuser%03d" % i for i in itertools.count()).next

        new_users = []
        for row in query:
            pid, name, vorname, strasse, plz, ort, tel1, tel2, email, geburtsdatum, confirmed, timestamp, \
            uid, pwd, lvl, _ = row

            if uid is None:
                uid = newid()
                #uid = email.decode("latin-1")
            else:
                uid = uid.decode("latin-1")

            user = User(username=uid)
            new_users.append(user)

        # bulk_create groups everything into a single query. Post-create events won't be sent.
        User.objects.bulk_create(new_users)

        new_locos = []
        users = sorted(User.objects.all(), key=lambda u: u.id)
        users = users[1:] # kick out super user
        num_unique_locos = 0
        total_locos = 0
        cnt = 0

        for user, row in zip(users, query):
            pid, name, vorname, strasse, plz, ort, tel1, tel2, email, geburtsdatum, confirmed, timestamp, \
            uid, pwd, lvl, _ = self.decode_row(row)

            total_locos += 1
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

            num_unique_locos += 1
            new_locos.append(loco)

            # keep this data around to associate locos with jobs later
            self.userids[pid] = user.id


        Loco.objects.bulk_create(new_locos)

        print '***************************************************************'
        print 'users and locos migrated'
        print '***************************************************************'

    def create_taetigkeitsbereiche(self):

        print '***************************************************************'
        print 'Migrating Taetigkeitsbereiche'
        print '***************************************************************'

        query = list(self.query("SELECT * FROM lux_funktion ")) 	
        new_taetigkeitsbereiche = []

        from _koordinatoren import koordinatoren

        for row in query:
            id, name, description, type, showorder = self.decode_row(row)
            
            if name not in koordinatoren:
                print "not migrating bereich %s" % name
                continue

            email = koordinatoren[name]
            try:
                coordinator = Loco.objects.get(email=email)
            except Exception:
                print "cannot find loco with email %s" %email
                #coordinator = Loco.objects.get(pk=1)
                coordinator = Loco.objects.get(user_id=1)
            core = name in ("ernten", "abpacken", "verteilen")
            hidden = name in ("adminbuchhaltung",)

            taetigkeitsbereich = Taetigkeitsbereich(name=name,
                                                    description=description,
                                                    coordinator=coordinator,
                                                    core=core)

            new_taetigkeitsbereiche.append(taetigkeitsbereich)


        Taetigkeitsbereich.objects.bulk_create(new_taetigkeitsbereiche)

        print '***************************************************************'
        print 'Taetigkeitsbereiche migrated'
        print '***************************************************************'

    def create_depots(self):

        print '***************************************************************'
        print 'Migrating Depots'
        print '***************************************************************'

        query = list(self.query("SELECT id, 'SomeCode' as code, name, "
                                "description, 9999 as contact_id,24 as weekday, "
                                "case when instr(data,',')>0 "
                                "then substring(data,1, instr(data,',')-1) "
                                "else name "
                                "end as addr_street, "
                                "addr_zipcode, "
                                "case when instr(data,',')>0 "
                                "then substring(data,instr(data,',')+6,length(data)-instr(data,',')) "
                                "else 'Zürich' "
                                "end as addr_location "
                                "FROM ( "
                                "SELECT id "
                                ",case when instr(description,':')>0 "
                                "then substring(description,1,instr(description,':')-1) "
                                "else  case when instr(description,',')>0 "
                                "then substring(description,1,instr(description,',')-1) "
                                "else 'No Name' end "
                                "end as name "
                                ",description"
                                ",name as addr_zipcode "
                                ",case when instr(description,':')>0 "
                                "then substring(description,instr(description,':')+1,"
                                "length(description)-instr(description,':')) "
                                "else  case when instr(description,',')>0 "
                                "then substring(description,instr(description,',')+1,"
                                "length(description)-instr(description,',')) "
                                "else CONCAT('-, ',description) end "
                                "end as data "
                                "FROM lu_depot "
                                ") dt"))

        new_depots = [] 
        #locos = sorted(Loco.objects.all(), key=lambda u: u.id)
        loco = User.objects.get(id=1).loco

        newid = ("d%02d" % i for i in itertools.count(1)).next

        for row in query:
            id, code, name, description, contact_id, weekday, addr_street, addr_zipcode, addr_location = self.decode_row(row)
            if name=='No Name':
                name=name+addr_zipcode
            code = newid()

            from _depots import depot_wochentag
            weekday = depot_wochentag[name]
            if weekday == -1:
                print "Skipping depot %s (no longer exists?)" % name
                continue

            depot = Depot(code=code,
                          name=name,
                          description=description,
                          contact=loco,
                          weekday=weekday,
                          addr_street=addr_street,
                          addr_zipcode=addr_zipcode,
                          addr_location=addr_location,
                          latitude="47.345",
                          longitude="8.549")

            new_depots.append(depot)

        Depot.objects.bulk_create(new_depots)

        print '***************************************************************'
        print 'Depots migrated'
        print '***************************************************************'

    def create_taetigkeitsbereich_locos(self):

        print '***************************************************************'
        print 'Building Taetigkeitsbereiche_Locos'
        print '***************************************************************'

        query = list(self.query("select pu.*,funktion, "
                                    "case when substr(funktion,1,1)=1 then 'ernten' else '' end fkt1, "
                                    "case when substr(funktion,3,1)=1 then 'abpacken' else '' end fkt2, "
                                    "case when substr(funktion,5,1)=1 then 'verteilen' else '' end fkt3, "
                                    "case when substr(funktion,7,1)=1 then 'garten' else '' end fkt4, "
                                    "case when substr(funktion,9,1)=1 then 'rand' else '' end fkt5, "
                                    "case when substr(funktion,11,1)=1 then 'freitag' else '' end fkt6, "
                                    "case when substr(funktion,13,1)=1 then 'springer' else '' end fkt7, "
                                    "case when substr(funktion,15,1)=1 then 'wochenend' else '' end fkt8, "
                                    "case when substr(funktion,17,1)=1 then 'infrastruktur' else '' end fkt9, "
                                    "case when substr(funktion,19,1)=1 then 'gastrofeste' else '' end fkt10, "
                                    "case when substr(funktion,21,1)=1 then 'adminbuchhaltung' else '' end fkt11, "
                                    "case when substr(funktion,23,1)=1 then 'beeren' else '' end fkt12, "
                                    "case when substr(funktion,25,1)=1 then 'pilze' else '' end fkt13, "
                                    "case when substr(funktion,27,1)=1 then 'kraeuterblumen' else '' end fkt14 "
                                    "from funktion f "
                                    "join "
                                    "( "
                                    "select pid,vorname,name "
                                    "from "
                                    "(SELECT  p.* "
                                    "FROM person p "
                                    "LEFT OUTER JOIN usr u "
                                    "ON p.pid = u.pid "
                                    "where u.pid is not null "
                                    "UNION "
                                    "SELECT p.* "
                                    "FROM person p "
                                    "RIGHT OUTER JOIN usr u "
                                    "ON p.pid = u.pid "
                                    "where p.pid is not null "
                                    ") dt "
                                    "where pid is not null "
                                    ") pu "
                                    "on f.pid=pu.pid "
                                    "order by pid "))

        new_bereiche_locos = defaultdict(list)

        locos = sorted(Loco.objects.all(), key=lambda l: l.id)
        taetigkeitsbereiche = sorted(Taetigkeitsbereich.objects.all(), key=lambda ta: ta.id)

        for row in query:
            pid,vorname,name,funktion,fkt1,fkt2,fkt3,fkt4,fkt5,fkt6,fkt7,fkt8,fkt9,fkt10,fkt11,fkt12,fkt13, \
            fkt14 = self.decode_row(row)

            for loco in locos:
                if name == loco.last_name and vorname == loco.first_name:
                    for fkt in (fkt1, fkt2, fkt3, fkt4, fkt5, fkt6, fkt7, fkt8, 
                                fkt9, fkt10, fkt11, fkt12, fkt13, fkt14):
                        # if fkt is "" it is thrown into dict anyway and ignored afterward.
                        new_bereiche_locos[fkt].append(loco)

        new_bereichlocos = []
        for bereich in Taetigkeitsbereich.objects.all():
            for loco in new_bereiche_locos[bereich.name]:
                bl = bereich.locos.through(taetigkeitsbereich=bereich, loco=loco)
                new_bereichlocos.append(bl)
            #bereich.locos = new_bereiche_locos[bereich.name]

        bereich.locos.through.objects.bulk_create(new_bereichlocos)

        print '***************************************************************'
        print 'Teatigkeitsbereiche_Locos built'
        print '***************************************************************'

    def create_jobtypes(self):

        print '***************************************************************'
        print 'Migrating JobTypes'
        print '***************************************************************'

        from _create_jobtyps import create_jobtyps

        create_jobtyps()

        print '***************************************************************'
        print 'JobTypes migrated'
        print '***************************************************************'

    def create_jobs(self):

        print '***************************************************************'
        print 'Migrating Jobs'
        print '***************************************************************'

        query = list(self.query("SELECT * "
                                "from lux_job "
                                "where active=1"))

        new_jobs = []
        for row in query:
            jid, name, description, units, cat, start, loc, created_on, created_by, active, beans = self.decode_row(row)

            start = datetime.datetime.fromtimestamp(int(start) + 7*60*60)
            if datetime.date(2014, 3, 4) < datetime.date(start.year, start.month, start.day) < datetime.date(2014, 3, 30):
                start -= datetime.timedelta(hours=1)
            start = timezone.make_aware(start, timezone.get_current_timezone())

            try:
                typ = JobTyp.objects.get(name__iexact=name)
            except Exception:
                print "No jobtyp with name %s" % name
                continue

            job = Job(typ=typ,
                      slots=units,
                      time=start)

            new_jobs.append(job)

        Job.objects.bulk_create(new_jobs)

        # translate job ids from old to new db
        jobids = dict((row[0], job.id) for (job, row) in zip(Job.objects.all(), query))
        
        # now that jobs are created, associate locos that already registered themselves for the job
        
        # create reference time at start of year 2014
        delta = datetime.datetime(2014, 1, 1) - datetime.datetime.fromtimestamp(0)
        reference = delta.days * 86400 + delta.seconds

        query = self.query("SELECT j.pid, j.jid, j.units "
                           "  FROM job j "
                           "       JOIN lux_job lj "
                           "  ON j.jid=lj.jid "
                           "  WHERE lj.active=1")

        new_boehnlis = []
        for row in query:
            pid, jid, units = self.decode_row(row)

            if jid not in jobids:
                # assume job already done
                print "Cannot find job corresponding to old job %s" %jid
                continue
            if pid not in self.userids:
                print "Cannot find loco corresponding to person %s" %pid
                continue
                
            loco = Loco.objects.get(user_id=self.userids[pid])
            job = Job.objects.get(id=jobids[jid])
            b = Boehnli(job=job, loco=loco)
            new_boehnlis.append(b)

        Boehnli.objects.bulk_create(new_boehnlis)

        print '***************************************************************'
        print 'Jobs migrated'
        print '***************************************************************'

    def create_extraabotypes(self):

        print '***************************************************************'
        print 'Migrating ExtraAboTypes'
        print '***************************************************************'

        query = list(self.query("SELECT * "
                                "FROM lux_abo "
                                "WHERE showorder is not null "
                                "order by showorder"))

        new_extraabotypes = []

        for row in query:
            id, name, description, type, price, showorder = self.decode_row(row)

            extraabotype = ExtraAboType(name=name,
                                        description=description)

            new_extraabotypes.append(extraabotype)

        ExtraAboType.objects.bulk_create(new_extraabotypes)

        print '***************************************************************'
        print 'ExtraAboTypes migrated'
        print '***************************************************************'

    def create_abos(self):

        print '***************************************************************'
        print 'Migrating Abos'
        print '***************************************************************'

        query = list(self.query("SELECT a.pid as abopid, anteilschein, abo as abostr, abomit as abomitpid, "
                                "a.timestamp, p.name as last_name, p.vorname as first_name, "
                                "p.email, description, "
                                "case when (substr(abo,1,1)=1 and substr(abo,3,1)=0) then 1 "
                                "else case when (substr(abo,1,1)=1 and substr(abo,3,1)=1) then 3 "
                                "else case when substr(abo,3,1)=1 then 2 "
                                "else case when substr(abo,3,1)=2 then 4 "
                                "end "
                                "end "
                                "end "
                                "end as groesse, "
                                "p1.name as abomitname, "
                                "p1.vorname as abomitvorname, "
                                "p1.email as abomitemail "
                                "FROM abo a "
                                "JOIN person p "
                                "ON a.pid=p.pid "
                                "JOIN lu_depot ld "
                                "ON a.depot=ld.id "
                                "LEFT OUTER JOIN person p1 "
                                "ON a.abomit = p1.pid "
                                "where (substr(abo,1,1)=1 "
                                "or substr(abo,3,1)=1 "
                                "or substr(abo,19,1)=1) "
                                "or (substr(abo,1,1)=1 and substr(abo,3,1)=1)"
                                "or substr(abo,3,1) = 2"))

        new_abos = []
        primary_to_all = defaultdict(list)

        for row in query:
            abopid, anteilschein, abostr, abomitpid, timestamp, last_name, first_name, email, \
            description, groesse, abomitname, abomitvorname, abomitemail = self.decode_row(row)

            if abomitemail is not None:
                primary_to_all[email].append(abomitemail)

            try:
                locoidlookup=Loco.objects.get(email=email)
            except ObjectDoesNotExist:
                print 'Warning: Loco ', last_name, first_name, email, ' not found, skipping abo'
                continue
            except MultipleObjectsReturned:
                print 'Warning: More than one Loco for ', last_name, first_name, email, ", skipping abo"
                continue

            try:
                depotidlookup=Depot.objects.get(description=description)
            except ObjectDoesNotExist:
                print 'Warning: No Depot found for ', last_name, first_name, email, ", skipping abo"
                continue

            abo = Abo(depot_id=depotidlookup.id,
                      primary_loco_id=locoidlookup.id,
                      groesse=groesse)

            new_abos.append(abo)


        Abo.objects.bulk_create(new_abos)

        new_abolocos = []
        abos = sorted(Abo.objects.all(), key=lambda a: a.id)
        for abo in abos:
            try:
                loco=Loco.objects.get(id=abo.primary_loco.id)
            except ObjectDoesNotExist:
                print 'Warning: Loco ', abo.primary_loco_id, ' not found'
                continue

            loco.abo=abo
            loco.save()
            new_abolocos.append(loco)

            for mitemail in primary_to_all[loco.email]:
                try:
                    mit_loco = Loco.objects.get(email=abomitemail)
                    mit_loco.abo=abo
                    mit_loco.save()
                except MultipleObjectsReturned:
                    print 'Warning: More than one abomit_Loco for ', abomitname, ' ', abomitvorname,\
                          ' ', abomitemail

        print '***************************************************************'
        print 'Abos migrated'
        print '***************************************************************'

    def create_abo_extra_abos(self):

        print '***************************************************************'
        print 'Building Abo_Extra_Abos'
        print '***************************************************************'

        query = list(self.query("SELECT a.pid as abopid, anteilschein, "
                                "p.name as last_name, p.vorname as first_name, "
                                "p.email, "
                                "case when substr(abo,5,1)='1' then 'obst_gross' else '' end eat7, "
                                "case when substr(abo,7,1)='1' then 'eier_4' else '' end eat1, "
                                "case when substr(abo,9,1)='1' then 'eier_6' else '' end eat2, "
                                "case when substr(abo,11,1)='1' then 'kaese_1' else '' end eat3, "
                                "case when substr(abo,13,1)='1' then 'obst_klein' else '' end eat6, "
                                "case when substr(abo,15,1)='1' then 'kaese_05' else '' end eat4, "
                                "case when substr(abo,17,1)='1' then 'kaese_025' else '' end eat5 "
                                "FROM abo a "
                                "JOIN person p "
                                "ON a.pid=p.pid "))

        # map each email to its corresponding row
        d = dict((row[4], row) for row in query)

        new_aboextraabos = []
        for abo in Abo.objects.all():
            loco = abo.primary_loco
            key = loco.email
            if key not in d:
                print "No extraabo data found for abo <%s> corresponding to <%s>" %(abo, loco)
                continue

            row = d[key]

            abopid, anteilschein, last_name, first_name, email, eat1, eat2, eat3, eat4, eat5,\
            eat6, eat7 = self.decode_row(row)

            new_eattypes0_abos = []
            # each eat is either the name of an extraabotype or "", see query above
            names = set((eat1, eat2, eat3, eat4, eat5, eat6, eat7)) - set(("",))

            for extra in ExtraAboType.objects.filter(name__in=names):
                aea = Abo.extra_abos.through(abo=abo, extraabotype=extra)
                new_aboextraabos.append(aea)

        Abo.extra_abos.through.objects.bulk_create(new_aboextraabos)

        print '***************************************************************'
        print 'Abo_Extra_Abos built'
        print '***************************************************************'

    def create_anteilscheine(self):

        print '***************************************************************'
        print 'Building Anteilscheine'
        print '***************************************************************'

        print "skipping for now!"
        return


        query = list(self.query("select a.pid as abopid, anteilschein, p.name as last_name, "
                                "p.vorname as first_name,p.email "
                                "from abo a "
                                "join person p "
                                "on a.pid=p.pid"))

        for row in query:
            abopid, anteilschein,last_name, first_name, email = self.decode_row(row)

            i = 0
            new_anteilscheine = []

            while i < anteilschein:
                try:
                    loco=Loco.objects.get(last_name=last_name,first_name=first_name,email=email)
                    anteilscheine = Anteilschein(paid=1,
                                                 loco_id=loco.id)
                    new_anteilscheine.append(anteilscheine)
                    i = i+1
                except ObjectDoesNotExist:
                    i = i+1
                    print 'No Abo found for primary_loco_id: ',loco.id
                except MultipleObjectsReturned:
                    i = i+1
                    print 'Warning: More than one Abo for ', loco.id, ' ', loco.last_name, ' ', \
                    loco.first_name, ' ', loco.email

            Anteilschein.objects.bulk_create(new_anteilscheine)

        print '***************************************************************'
        print 'Anteilscheine built'
        print '***************************************************************'
