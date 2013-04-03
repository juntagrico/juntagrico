# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Depot'
        db.create_table(u'loco_app_depot', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'loco_app', ['Depot'])


    def backwards(self, orm):
        # Deleting model 'Depot'
        db.delete_table(u'loco_app_depot')


    models = {
        u'loco_app.depot': {
            'Meta': {'object_name': 'Depot'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['loco_app']