# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AboHistory'
        db.create_table(u'loco_app_abohistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('abo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['loco_app.Abo'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('start', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'loco_app', ['AboHistory'])

        # Adding model 'ExtraAboType'
        db.create_table(u'loco_app_extraabotype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal(u'loco_app', ['ExtraAboType'])

        # Adding M2M table for field extra_abos on 'Abo'
        db.create_table(u'loco_app_abo_extra_abos', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('abo', models.ForeignKey(orm[u'loco_app.abo'], null=False)),
            ('extraabotype', models.ForeignKey(orm[u'loco_app.extraabotype'], null=False))
        ))
        db.create_unique(u'loco_app_abo_extra_abos', ['abo_id', 'extraabotype_id'])


        # Changing field 'AboType.description'
        db.alter_column(u'loco_app_abotype', 'description', self.gf('django.db.models.fields.CharField')(max_length=1000))
        # Removing M2M table for field abos on 'Loco'
        db.delete_table('loco_app_loco_abos')


        # Changing field 'Depot.description'
        db.alter_column(u'loco_app_depot', 'description', self.gf('django.db.models.fields.CharField')(max_length=1000))

    def backwards(self, orm):
        # Deleting model 'AboHistory'
        db.delete_table(u'loco_app_abohistory')

        # Deleting model 'ExtraAboType'
        db.delete_table(u'loco_app_extraabotype')

        # Removing M2M table for field extra_abos on 'Abo'
        db.delete_table('loco_app_abo_extra_abos')


        # Changing field 'AboType.description'
        db.alter_column(u'loco_app_abotype', 'description', self.gf('django.db.models.fields.CharField')(max_length=10000))
        # Adding M2M table for field abos on 'Loco'
        db.create_table(u'loco_app_loco_abos', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('loco', models.ForeignKey(orm[u'loco_app.loco'], null=False)),
            ('abo', models.ForeignKey(orm[u'loco_app.abo'], null=False))
        ))
        db.create_unique(u'loco_app_loco_abos', ['loco_id', 'abo_id'])


        # Changing field 'Depot.description'
        db.alter_column(u'loco_app_depot', 'description', self.gf('django.db.models.fields.CharField')(max_length=10000))

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
            'extra_abos': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['loco_app.ExtraAboType']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'abo_history'", 'symmetrical': 'False', 'through': u"orm['loco_app.AboHistory']", 'to': u"orm['auth.User']"})
        },
        u'loco_app.abohistory': {
            'Meta': {'object_name': 'AboHistory'},
            'abo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['loco_app.Abo']"}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'loco_app.abotype': {
            'Meta': {'object_name': 'AboType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'loco_app.depot': {
            'Meta': {'object_name': 'Depot'},
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'loco_app.extraabotype': {
            'Meta': {'object_name': 'ExtraAboType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'loco_app.loco': {
            'Meta': {'object_name': 'Loco'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'loco'", 'unique': 'True', 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['loco_app']