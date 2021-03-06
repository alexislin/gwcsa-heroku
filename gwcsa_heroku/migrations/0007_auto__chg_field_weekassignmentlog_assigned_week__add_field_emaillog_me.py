# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'WeekAssignmentLog.assigned_week'
        db.alter_column(u'gwcsa_heroku_weekassignmentlog', 'assigned_week', self.gf('django.db.models.fields.CharField')(max_length=1, null=True))
        # Adding field 'EmailLog.member'
        db.add_column(u'gwcsa_heroku_emaillog', 'member',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gwcsa_heroku.Member'], null=True),
                      keep_default=False)


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'WeekAssignmentLog.assigned_week'
        raise RuntimeError("Cannot reverse this migration. 'WeekAssignmentLog.assigned_week' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'WeekAssignmentLog.assigned_week'
        db.alter_column(u'gwcsa_heroku_weekassignmentlog', 'assigned_week', self.gf('django.db.models.fields.CharField')(max_length=1))
        # Deleting field 'EmailLog.member'
        db.delete_column(u'gwcsa_heroku_emaillog', 'member_id')


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
            'farmigo_share_description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'farmigo_signup_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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