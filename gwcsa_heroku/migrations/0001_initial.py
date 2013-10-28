# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TimestampedModel'
        db.create_table(u'gwcsa_heroku_timestampedmodel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'gwcsa_heroku', ['TimestampedModel'])

        # Adding model 'WorkShift'
        db.create_table(u'gwcsa_heroku_workshift', (
            (u'timestampedmodel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gwcsa_heroku.TimestampedModel'], unique=True, primary_key=True)),
            ('season', self.gf('django.db.models.fields.PositiveIntegerField')(default=2014)),
        ))
        db.send_create_signal(u'gwcsa_heroku', ['WorkShift'])


    def backwards(self, orm):
        # Deleting model 'TimestampedModel'
        db.delete_table(u'gwcsa_heroku_timestampedmodel')

        # Deleting model 'WorkShift'
        db.delete_table(u'gwcsa_heroku_workshift')


    models = {
        u'gwcsa_heroku.timestampedmodel': {
            'Meta': {'object_name': 'TimestampedModel'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'gwcsa_heroku.workshift': {
            'Meta': {'object_name': 'WorkShift', '_ormbases': [u'gwcsa_heroku.TimestampedModel']},
            'season': ('django.db.models.fields.PositiveIntegerField', [], {'default': '2014'}),
            u'timestampedmodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gwcsa_heroku.TimestampedModel']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['gwcsa_heroku']