# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'WorkShiftDateTime'
        db.delete_table(u'gwcsa_heroku_workshiftdatetime')

        # Deleting model 'WorkShift'
        db.delete_table(u'gwcsa_heroku_workshift')

        # Deleting model 'MemberWorkShift'
        db.delete_table(u'gwcsa_heroku_memberworkshift')

        # Deleting model 'WeekAssignmentLog'
        db.delete_table(u'gwcsa_heroku_weekassignmentlog')


    def backwards(self, orm):
        # Adding model 'WorkShiftDateTime'
        db.create_table(u'gwcsa_heroku_workshiftdatetime', (
            ('num_members_required', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('end_time', self.gf('django.db.models.fields.TimeField')()),
            ('start_time', self.gf('django.db.models.fields.TimeField')()),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('shift', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gwcsa_heroku.WorkShift'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'gwcsa_heroku', ['WorkShiftDateTime'])

        # Adding model 'WorkShift'
        db.create_table(u'gwcsa_heroku_workshift', (
            ('num_required_per_member', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('season', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gwcsa_heroku.Season'])),
            ('location2', self.gf('django.db.models.fields.CharField')(default='', max_length=120)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('day', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('note', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=120)),
        ))
        db.send_create_signal(u'gwcsa_heroku', ['WorkShift'])

        # Adding model 'MemberWorkShift'
        db.create_table(u'gwcsa_heroku_memberworkshift', (
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('workshift_date_time', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gwcsa_heroku.WorkShiftDateTime'])),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gwcsa_heroku.Member'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'gwcsa_heroku', ['MemberWorkShift'])

        # Adding model 'WeekAssignmentLog'
        db.create_table(u'gwcsa_heroku_weekassignmentlog', (
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gwcsa_heroku.Member'])),
            ('assigned_week', self.gf('django.db.models.fields.CharField')(max_length=1, null=True)),
            ('module_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'gwcsa_heroku', ['WeekAssignmentLog'])


    models = {
        u'gwcsa_heroku.emaillog': {
            'Meta': {'object_name': 'EmailLog'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gwcsa_heroku.Member']", 'null': 'True'}),
            'status_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '350'}),
            'to_email': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'to_name': ('django.db.models.fields.CharField', [], {'max_length': '210'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'gwcsa_heroku.member': {
            'Meta': {'object_name': 'Member'},
            'assigned_week': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'day': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'farmigo_last_modified_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'farmigo_share_description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'farmigo_signup_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'has_biweekly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_weekly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'season': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gwcsa_heroku.Season']"}),
            'secondary_email': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'secondary_first_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'secondary_last_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'gwcsa_heroku.season': {
            'Meta': {'object_name': 'Season'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'2018'", 'max_length': '6'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'gwcsa_heroku.share': {
            'Meta': {'object_name': 'Share'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gwcsa_heroku.Member']"}),
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['gwcsa_heroku']