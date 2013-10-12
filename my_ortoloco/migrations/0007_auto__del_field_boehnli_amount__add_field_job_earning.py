# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Boehnli.amount'
        db.delete_column(u'my_ortoloco_boehnli', 'amount')

        # Adding field 'Job.earning'
        db.add_column(u'my_ortoloco_job', 'earning',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=1),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Boehnli.amount'
        db.add_column(u'my_ortoloco_boehnli', 'amount',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=1),
                      keep_default=False)

        # Deleting field 'Job.earning'
        db.delete_column(u'my_ortoloco_job', 'earning')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'my_ortoloco.abo': {
            'Meta': {'object_name': 'Abo'},
            'depot': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['my_ortoloco.Depot']", 'on_delete': 'models.PROTECT'}),
            'extra_abos': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['my_ortoloco.ExtraAboType']", 'null': 'True', 'blank': 'True'}),
            'groesse': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'primary_loco': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'abo_primary'", 'null': 'True', 'to': u"orm['my_ortoloco.Loco']"})
        },
        u'my_ortoloco.anteilschein': {
            'Meta': {'object_name': 'Anteilschein'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        u'my_ortoloco.audit': {
            'Meta': {'object_name': 'Audit'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'field': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'source_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'source_set'", 'to': u"orm['contenttypes.ContentType']"}),
            'target_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'target_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'target_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'my_ortoloco.boehnli': {
            'Meta': {'object_name': 'Boehnli'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['my_ortoloco.Job']"}),
            'loco': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['my_ortoloco.Loco']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'my_ortoloco.depot': {
            'Meta': {'object_name': 'Depot'},
            'addr_location': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'addr_street': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'addr_zipcode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'on_delete': 'models.PROTECT'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'weekday': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'my_ortoloco.extraabotype': {
            'Meta': {'object_name': 'ExtraAboType'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'my_ortoloco.job': {
            'Meta': {'object_name': 'Job'},
            'earning': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slots': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'typ': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['my_ortoloco.JobTyp']", 'on_delete': 'models.PROTECT'})
        },
        u'my_ortoloco.jobtyp': {
            'Meta': {'object_name': 'JobTyp'},
            'bereich': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['my_ortoloco.Taetigkeitsbereich']", 'on_delete': 'models.PROTECT'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '1000'}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'my_ortoloco.loco': {
            'Meta': {'object_name': 'Loco'},
            'abo': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'locos'", 'null': 'True', 'to': u"orm['my_ortoloco.Abo']"}),
            'addr_location': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'addr_street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'addr_zipcode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'loco'", 'unique': 'True', 'to': u"orm['auth.User']"})
        },
        u'my_ortoloco.taetigkeitsbereich': {
            'Meta': {'object_name': 'Taetigkeitsbereich'},
            'coordinator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'on_delete': 'models.PROTECT'}),
            'core': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'taetigkeitsbereiche'", 'symmetrical': 'False', 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['my_ortoloco']