# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Link.name'
        db.delete_column(u'static_ortoloco_link', 'name')

        # Adding field 'Link.titel'
        db.add_column(u'static_ortoloco_link', 'titel',
                      self.gf('django.db.models.fields.CharField')(default='Beispieltitel', max_length=200),
                      keep_default=False)

        # Adding field 'Link.link'
        db.add_column(u'static_ortoloco_link', 'link',
                      self.gf('django.db.models.fields.CharField')(default='http://example.ch', max_length=200),
                      keep_default=False)


        # Changing field 'StaticContent.content'
        db.alter_column(u'static_ortoloco_staticcontent', 'content', self.gf('tinymce.models.HTMLField')(max_length=10000))

    def backwards(self, orm):
        # Adding field 'Link.name'
        db.add_column(u'static_ortoloco_link', 'name',
                      self.gf('django.db.models.fields.CharField')(default='blabla', max_length=200),
                      keep_default=False)

        # Deleting field 'Link.titel'
        db.delete_column(u'static_ortoloco_link', 'titel')

        # Deleting field 'Link.link'
        db.delete_column(u'static_ortoloco_link', 'link')


        # Changing field 'StaticContent.content'
        db.alter_column(u'static_ortoloco_staticcontent', 'content', self.gf('django.db.models.fields.TextField')(max_length=10000))

    models = {
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