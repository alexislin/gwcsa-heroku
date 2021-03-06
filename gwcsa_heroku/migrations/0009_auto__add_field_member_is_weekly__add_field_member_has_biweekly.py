# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Member.is_weekly'
        db.add_column(u'gwcsa_heroku_member', 'is_weekly',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Member.has_biweekly'
        db.add_column(u'gwcsa_heroku_member', 'has_biweekly',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Member.is_weekly'
        db.delete_column(u'gwcsa_heroku_member', 'is_weekly')

        # Deleting field 'Member.has_biweekly'
        db.delete_column(u'gwcsa_heroku_member', 'has_biweekly')


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
        u'gwcsa_heroku.share': {
            'Meta': {'object_name': 'Share'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gwcsa_heroku.Member']"}),
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'gwcsa_heroku.weekassignmentlog': {
            'Meta': {'object_name': 'WeekAssignmentLog'},
            'assigned_week': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gwcsa_heroku.Member']"}),
            'module_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
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
            'note': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
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