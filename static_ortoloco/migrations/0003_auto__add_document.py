# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Document'
        db.create_table(u'static_ortoloco_document', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='Beispieltitel', max_length=200)),
            ('document', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=400)),
        ))
        db.send_create_signal(u'static_ortoloco', ['Document'])


    def backwards(self, orm):
        # Deleting model 'Document'
        db.delete_table(u'static_ortoloco_document')


    models = {
        u'static_ortoloco.document': {
            'Meta': {'object_name': 'Document'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'document': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'Beispieltitel'", 'max_length': '200'})
        },
        u'static_ortoloco.download': {
            'Meta': {'object_name': 'Download'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mediafile': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'static_ortoloco.link': {
            'Meta': {'object_name': 'Link'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'default': "'http://example.ch'", 'max_length': '200'}),
            'titel': ('django.db.models.fields.CharField', [], {'default': "'Beispieltitel'", 'max_length': '200'})
        },
        u'static_ortoloco.media': {
            'Meta': {'object_name': 'Media'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mediafile': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'year': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        u'static_ortoloco.politoloco': {
            'Meta': {'object_name': 'Politoloco'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'static_ortoloco.staticcontent': {
            'Meta': {'object_name': 'StaticContent'},
            'content': ('tinymce.models.HTMLField', [], {'default': "''", 'max_length': '10000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['static_ortoloco']