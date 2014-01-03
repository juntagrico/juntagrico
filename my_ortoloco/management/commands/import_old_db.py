# -*- coding: utf-8 -*-
import datetime
import re
import itertools

import MySQLdb
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
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
                                "WHERE p.pid is null "
                                "order by name,vorname,email, confirmed desc"))

        # everything wer're throwing out here is bad data of some form...
        oldsize = len(query)
        #query = [row for row in query if None not in (row[0], row[15])]
        query = [row for row in query if None not in (row[0],)]
        if len(query) < oldsize:
            print "warning: some inconsistent data, ignoring..."

        newid = (u"fake_email_%03d@ortoloco.ch" % i for i in itertools.count()).next

        new_users = []
        for row in query:
            pid, name, vorname, strasse, plz, ort, tel1, tel2, email, geburtsdatum, confirmed, timestamp, \
            uid, pwd, lvl, _ = row
            
            if uid is None:
                uid = newid()
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
        chk_str = ''

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

            if chk_str != name+vorname+email: #filter non unique locos
                chk_str = name+vorname+email
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
            else:
                print 'Warning: Non unique Loco: ', name, vorname, email, 'only one instance migrated'



        print 'Unique: ', num_unique_locos
        print 'Total: ', total_locos

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
        locos = sorted(Loco.objects.all(), key=lambda u: u.id)
        loco_id=locos[0].id

        newid = ("d%02d" % i for i in itertools.count(1)).next

        for row in query:
            id, code, name, description, contact_id, weekday, addr_street, addr_zipcode, addr_location = self.decode_row(row)

            if name=='No Name':
                name=name+addr_zipcode
            code = newid()
            depot = Depot(code=code,
                          name=name,
                          description=description,
                          contact_id=loco_id,
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
        print 'Building Teatigkeitsbereiche_Locos'
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

        new_taetigkeitsbereich0_locos = []
        new_taetigkeitsbereich1_locos = []
        new_taetigkeitsbereich2_locos = []
        new_taetigkeitsbereich3_locos = []
        new_taetigkeitsbereich4_locos = []
        new_taetigkeitsbereich5_locos = []
        new_taetigkeitsbereich6_locos = []
        new_taetigkeitsbereich7_locos = []
        new_taetigkeitsbereich8_locos = []
        new_taetigkeitsbereich9_locos = []
        new_taetigkeitsbereich10_locos = []
        new_taetigkeitsbereich11_locos = []

        locos = sorted(Loco.objects.all(), key=lambda l: l.id)
        taetigkeitsbereiche = sorted(Taetigkeitsbereich.objects.all(), key=lambda ta: ta.id)

        for row in query:
            pid,vorname,name,funktion,fkt1,fkt2,fkt3,fkt4,fkt5,fkt6,fkt7,fkt8,fkt9,fkt10,fkt11,fkt12,fkt13, \
            fkt14 = self.decode_row(row)

            for loco in locos:
                if name == loco.last_name and vorname == loco.first_name:
                    if fkt1 == taetigkeitsbereiche[0].name:
                        new_taetigkeitsbereich0_locos.append(loco.id)
                    if fkt2 == taetigkeitsbereiche[1].name:
                        new_taetigkeitsbereich1_locos.append(loco.id)
                    if fkt3 == taetigkeitsbereiche[2].name:
                        new_taetigkeitsbereich2_locos.append(loco.id)
                    if fkt4 == taetigkeitsbereiche[3].name:
                        new_taetigkeitsbereich3_locos.append(loco.id)
                    if fkt5 == taetigkeitsbereiche[4].name:
                        new_taetigkeitsbereich4_locos.append(loco.id)
                    if fkt6 == taetigkeitsbereiche[5].name:
                        new_taetigkeitsbereich5_locos.append(loco.id)
                    if fkt7 == taetigkeitsbereiche[6].name:
                        new_taetigkeitsbereich6_locos.append(loco.id)
                    if fkt8 == taetigkeitsbereiche[7].name:
                        new_taetigkeitsbereich7_locos.append(loco.id)
                    if fkt9 == taetigkeitsbereiche[8].name:
                        new_taetigkeitsbereich8_locos.append(loco.id)
                    if fkt10 == taetigkeitsbereiche[9].name:
                        new_taetigkeitsbereich9_locos.append(loco.id)
                    if fkt11 == taetigkeitsbereiche[10].name:
                        new_taetigkeitsbereich10_locos.append(loco.id)
                    if fkt12 == taetigkeitsbereiche[11].name:
                        new_taetigkeitsbereich11_locos.append(loco.id)

        t0= Taetigkeitsbereich.objects.get(id=taetigkeitsbereiche[0].id)
        t0.locos=new_taetigkeitsbereich0_locos

        t1= Taetigkeitsbereich.objects.get(id=taetigkeitsbereiche[1].id)
        t1.locos=new_taetigkeitsbereich1_locos

        t2= Taetigkeitsbereich.objects.get(id=taetigkeitsbereiche[2].id)
        t2.locos=new_taetigkeitsbereich2_locos

        t3= Taetigkeitsbereich.objects.get(id=taetigkeitsbereiche[3].id)
        t3.locos=new_taetigkeitsbereich3_locos

        t4= Taetigkeitsbereich.objects.get(id=taetigkeitsbereiche[4].id)
        t4.locos=new_taetigkeitsbereich4_locos

        t5= Taetigkeitsbereich.objects.get(id=taetigkeitsbereiche[5].id)
        t5.locos=new_taetigkeitsbereich5_locos

        t6= Taetigkeitsbereich.objects.get(id=taetigkeitsbereiche[6].id)
        t6.locos=new_taetigkeitsbereich6_locos

        t7= Taetigkeitsbereich.objects.get(id=taetigkeitsbereiche[7].id)
        t7.locos=new_taetigkeitsbereich7_locos

        t8= Taetigkeitsbereich.objects.get(id=taetigkeitsbereiche[8].id)
        t8.locos=new_taetigkeitsbereich8_locos

        t9= Taetigkeitsbereich.objects.get(id=taetigkeitsbereiche[9].id)
        t9.locos=new_taetigkeitsbereich9_locos

        t10= Taetigkeitsbereich.objects.get(id=taetigkeitsbereiche[10].id)
        t10.locos=new_taetigkeitsbereich10_locos

        t11= Taetigkeitsbereich.objects.get(id=taetigkeitsbereiche[11].id)
        t11.locos=new_taetigkeitsbereich11_locos

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

        query = list(self.query("SELECT j.jid as jjid, timestamp, lj.jid as ljjid, name as jname, lj.units as slots "
                                "FROM job j "
                                "    JOIN lux_job lj "
                                "ON j.jid=lj.jid "
                                "WHERE lj.active=1"))

        new_jobs = []

        for row in query:
            jjid, timestamp, ljjid, jname, slots = self.decode_row(row)

            try:
                idlookup=JobTyp.objects.get(name=jname)
            except Exception:
                print "No jobtyp with name %s" % jname
                continue
            convdate=datetime.date.fromtimestamp(timestamp)

            typ=idlookup.id

            job = Job(typ_id=typ,
                      slots=slots,
                      time=convdate)

            new_jobs.append(job)

        Job.objects.bulk_create(new_jobs)

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

        for row in query:
            abopid, anteilschein, abostr, abomitpid, timestamp, last_name, first_name, email, \
            description, groesse, abomitname, abomitvorname, abomitemail = self.decode_row(row)

            try:
                locoidlookup=Loco.objects.get(last_name=last_name,first_name=first_name,email=email)

                depotidlookup=Depot.objects.get(description=description)

                abo = Abo(depot_id=depotidlookup.id,
                          primary_loco_id=locoidlookup.id,
                          groesse=groesse)

                new_abos.append(abo)

            except ObjectDoesNotExist:
                print 'Warning: Loco ', last_name, ' ', first_name, ' ', email, ' not found'
            except MultipleObjectsReturned:
                print 'Warning: More than one Loco for ', last_name, ' ', first_name, ' ', email

        Abo.objects.bulk_create(new_abos)

        abos = sorted(Abo.objects.all(), key=lambda a: a.id)

        for abo in abos:

            try:
                loco=Loco.objects.get(id=abo.primary_loco.id)
                loco.abo=abo
                loco.save()
                for row in query:
                    abopid, anteilschein, abostr, abomitpid, timestamp, last_name, first_name, email, \
                    description, groesse, abomitname, abomitvorname, abomitemail = self.decode_row(row)
                    if loco.email == email and abomitemail is not None:
                        try:
                            mit_loco = Loco.objects.get(last_name=abomitname,first_name=abomitvorname,email=abomitemail)
                            mit_loco.abo=abo
                            mit_loco.save()
                        except MultipleObjectsReturned:
                            print 'Warning: More than one abomit_Loco for ', abomitname, ' ', abomitvorname,\
                                  ' ', abomitemail
            except ObjectDoesNotExist:
                print 'Warning: Loco ', abo.primary_loco_id, ' not found'


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

        d = dict((row[4], row) for row in query)

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
            if eat1 != "": 
                new_eattypes0_abos.append(eat1)
            if eat2 != "": 
                new_eattypes0_abos.append(eat2)
            if eat3 != "": 
                new_eattypes0_abos.append(eat3)
            if eat4 != "": 
                new_eattypes0_abos.append(eat4)
            if eat5 != "": 
                new_eattypes0_abos.append(eat5)
            if eat6 != "": 
                new_eattypes0_abos.append(eat6)
            if eat7 != "":
                new_eattypes0_abos.append(eat7)

            abo.extra_abos = ExtraAboType.objects.filter(name__in=new_eattypes0_abos)

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
