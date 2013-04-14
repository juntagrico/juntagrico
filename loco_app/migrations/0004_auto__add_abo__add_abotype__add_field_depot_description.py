# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Abo'
        db.create_table(u'loco_app_abo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('abotype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['loco_app.AboType'])),
            ('depot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['loco_app.Depot'])),
        ))
        db.send_create_signal(u'loco_app', ['Abo'])

        # Adding model 'AboType'
        db.create_table(u'loco_app_abotype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=10000)),
        ))
        db.send_create_signal(u'loco_app', ['AboType'])

        # Adding M2M table for field abos on 'Loco'
        db.create_table(u'loco_app_loco_abos', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('loco', models.ForeignKey(orm[u'loco_app.loco'], null=False)),
            ('abo', models.ForeignKey(orm[u'loco_app.abo'], null=False))
        ))
        db.create_unique(u'loco_app_loco_abos', ['loco_id', 'abo_id'])

        # Adding field 'Depot.description'
        db.add_column(u'loco_app_depot', 'description',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10000),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Abo'
        db.delete_table(u'loco_app_abo')

        # Deleting model 'AboType'
        db.delete_table(u'loco_app_abotype')

        # Removing M2M table for field abos on 'Loco'
        db.delete_table('loco_app_loco_abos')

        # Deleting field 'Depot.description'
        db.delete_column(u'loco_app_depot', 'description')


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
        u'loco_app.abo': {
            'Meta': {'object_name': 'Abo'},
            'abotype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['loco_app.AboType']"}),
            'depot': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['loco_app.Depot']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'loco_app.abotype': {
            'Meta': {'object_name': 'AboType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '10000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'loco_app.depot': {
            'Meta': {'object_name': 'Depot'},
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'loco_app.loco': {
            'Meta': {'object_name': 'Loco'},
            'abos': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'locos'", 'symmetrical': 'False', 'to': u"orm['loco_app.Abo']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'loco'", 'unique': 'True', 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['loco_app']