# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Season'
        db.create_table(u'gwcsa_heroku_season', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='2014', max_length=6)),
        ))
        db.send_create_signal(u'gwcsa_heroku', ['Season'])

        # Adding model 'WorkShift'
        db.create_table(u'gwcsa_heroku_workshift', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('season', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gwcsa_heroku.Season'])),
            ('day', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('location2', self.gf('django.db.models.fields.CharField')(default='', max_length=120)),
            ('num_required_per_member', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'gwcsa_heroku', ['WorkShift'])

        # Adding model 'WorkShiftDateTime'
        db.create_table(u'gwcsa_heroku_workshiftdatetime', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('shift', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gwcsa_heroku.WorkShift'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('start_time', self.gf('django.db.models.fields.TimeField')()),
            ('end_time', self.gf('django.db.models.fields.TimeField')()),
            ('num_members_required', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'gwcsa_heroku', ['WorkShiftDateTime'])

        # Adding model 'Member'
        db.create_table(u'gwcsa_heroku_member', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('season', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gwcsa_heroku.Season'])),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=254)),
            ('phone', self.gf('django.db.models.fields.CharField')(default='', max_length=20)),
            ('day', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('farmigo_signup_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('farmigo_share_description', self.gf('django.db.models.fields.TextField')(default='')),
            ('is_weekly', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_biweekly', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('assigned_week', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('secondary_first_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('secondary_last_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('secondary_email', self.gf('django.db.models.fields.EmailField')(max_length=254)),
        ))
        db.send_create_signal(u'gwcsa_heroku', ['Member'])

        # Adding model 'MemberWorkShift'
        db.create_table(u'gwcsa_heroku_memberworkshift', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gwcsa_heroku.Member'])),
            ('workshift_date_time', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gwcsa_heroku.WorkShiftDateTime'])),
        ))
        db.send_create_signal(u'gwcsa_heroku', ['MemberWorkShift'])


    def backwards(self, orm):
        # Deleting model 'Season'
        db.delete_table(u'gwcsa_heroku_season')

        # Deleting model 'WorkShift'
        db.delete_table(u'gwcsa_heroku_workshift')

        # Deleting model 'WorkShiftDateTime'
        db.delete_table(u'gwcsa_heroku_workshiftdatetime')

        # Deleting model 'Member'
        db.delete_table(u'gwcsa_heroku_member')

        # Deleting model 'MemberWorkShift'
        db.delete_table(u'gwcsa_heroku_memberworkshift')


    models = {
        u'gwcsa_heroku.member': {
            'Meta': {'object_name': 'Member'},
            'assigned_week': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'day': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'farmigo_share_description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'farmigo_signup_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_biweekly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_weekly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'season': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gwcsa_heroku.Season']"}),
            'secondary_email': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'secondary_first_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'secondary_last_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'gwcsa_heroku.memberworkshift': {
            'Meta': {'object_name': 'MemberWorkShift'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gwcsa_heroku.Member']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'workshift_date_time': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gwcsa_heroku.WorkShiftDateTime']"})
        },
        u'gwcsa_heroku.season': {
            'Meta': {'object_name': 'Season'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'2014'", 'max_length': '6'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'gwcsa_heroku.workshift': {
            'Meta': {'object_name': 'WorkShift'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'day': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'location2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '120'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'num_required_per_member': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'season': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gwcsa_heroku.Season']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'gwcsa_heroku.workshiftdatetime': {
            'Meta': {'object_name': 'WorkShiftDateTime'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'end_time': ('django.db.models.fields.TimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_members_required': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'shift': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gwcsa_heroku.WorkShift']"}),
            'start_time': ('django.db.models.fields.TimeField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['gwcsa_heroku']