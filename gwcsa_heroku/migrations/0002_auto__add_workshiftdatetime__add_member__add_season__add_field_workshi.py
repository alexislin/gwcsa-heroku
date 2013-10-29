# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'WorkShiftDateTime'
        db.create_table(u'gwcsa_heroku_workshiftdatetime', (
            (u'timestampedmodel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gwcsa_heroku.TimestampedModel'], unique=True, primary_key=True)),
            ('shift', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gwcsa_heroku.WorkShift'])),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
            ('num_members_required', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'gwcsa_heroku', ['WorkShiftDateTime'])

        # Adding model 'Member'
        db.create_table(u'gwcsa_heroku_member', (
            (u'timestampedmodel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gwcsa_heroku.TimestampedModel'], unique=True, primary_key=True)),
            ('season', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gwcsa_heroku.Season'])),
        ))
        db.send_create_signal(u'gwcsa_heroku', ['Member'])

        # Adding model 'Season'
        db.create_table(u'gwcsa_heroku_season', (
            (u'timestampedmodel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gwcsa_heroku.TimestampedModel'], unique=True, primary_key=True)),
            ('year', self.gf('django.db.models.fields.PositiveIntegerField')(default=2014)),
        ))
        db.send_create_signal(u'gwcsa_heroku', ['Season'])

        # Adding field 'WorkShift.day'
        db.add_column(u'gwcsa_heroku_workshift', 'day',
                      self.gf('django.db.models.fields.CharField')(default='W', max_length=2),
                      keep_default=False)

        # Adding field 'WorkShift.name'
        db.add_column(u'gwcsa_heroku_workshift', 'name',
                      self.gf('django.db.models.fields.CharField')(default=datetime.datetime(2013, 10, 29, 0, 0), max_length=60),
                      keep_default=False)

        # Adding field 'WorkShift.location'
        db.add_column(u'gwcsa_heroku_workshift', 'location',
                      self.gf('django.db.models.fields.CharField')(default='foo', max_length=120),
                      keep_default=False)

        # Adding field 'WorkShift.location2'
        db.add_column(u'gwcsa_heroku_workshift', 'location2',
                      self.gf('django.db.models.fields.CharField')(default='foo', max_length=120),
                      keep_default=False)

        # Adding field 'WorkShift.num_required_per_member'
        db.add_column(u'gwcsa_heroku_workshift', 'num_required_per_member',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=1),
                      keep_default=False)


        # Renaming column for 'WorkShift.season' to match new field type.
        db.rename_column(u'gwcsa_heroku_workshift', 'season', 'season_id')
        # Changing field 'WorkShift.season'
        db.alter_column(u'gwcsa_heroku_workshift', 'season_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gwcsa_heroku.Season']))
        # Adding index on 'WorkShift', fields ['season']
        db.create_index(u'gwcsa_heroku_workshift', ['season_id'])


    def backwards(self, orm):
        # Removing index on 'WorkShift', fields ['season']
        db.delete_index(u'gwcsa_heroku_workshift', ['season_id'])

        # Deleting model 'WorkShiftDateTime'
        db.delete_table(u'gwcsa_heroku_workshiftdatetime')

        # Deleting model 'Member'
        db.delete_table(u'gwcsa_heroku_member')

        # Deleting model 'Season'
        db.delete_table(u'gwcsa_heroku_season')

        # Deleting field 'WorkShift.day'
        db.delete_column(u'gwcsa_heroku_workshift', 'day')

        # Deleting field 'WorkShift.name'
        db.delete_column(u'gwcsa_heroku_workshift', 'name')

        # Deleting field 'WorkShift.location'
        db.delete_column(u'gwcsa_heroku_workshift', 'location')

        # Deleting field 'WorkShift.location2'
        db.delete_column(u'gwcsa_heroku_workshift', 'location2')

        # Deleting field 'WorkShift.num_required_per_member'
        db.delete_column(u'gwcsa_heroku_workshift', 'num_required_per_member')


        # Renaming column for 'WorkShift.season' to match new field type.
        db.rename_column(u'gwcsa_heroku_workshift', 'season_id', 'season')
        # Changing field 'WorkShift.season'
        db.alter_column(u'gwcsa_heroku_workshift', 'season', self.gf('django.db.models.fields.PositiveIntegerField')())

    models = {
        u'gwcsa_heroku.member': {
            'Meta': {'object_name': 'Member', '_ormbases': [u'gwcsa_heroku.TimestampedModel']},
            'season': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gwcsa_heroku.Season']"}),
            u'timestampedmodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gwcsa_heroku.TimestampedModel']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'gwcsa_heroku.season': {
            'Meta': {'object_name': 'Season', '_ormbases': [u'gwcsa_heroku.TimestampedModel']},
            u'timestampedmodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gwcsa_heroku.TimestampedModel']", 'unique': 'True', 'primary_key': 'True'}),
            'year': ('django.db.models.fields.PositiveIntegerField', [], {'default': '2014'})
        },
        u'gwcsa_heroku.timestampedmodel': {
            'Meta': {'object_name': 'TimestampedModel'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'gwcsa_heroku.workshift': {
            'Meta': {'object_name': 'WorkShift', '_ormbases': [u'gwcsa_heroku.TimestampedModel']},
            'day': ('django.db.models.fields.CharField', [], {'default': "'W'", 'max_length': '2'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'location2': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'num_required_per_member': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'season': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gwcsa_heroku.Season']"}),
            u'timestampedmodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gwcsa_heroku.TimestampedModel']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'gwcsa_heroku.workshiftdatetime': {
            'Meta': {'object_name': 'WorkShiftDateTime', '_ormbases': [u'gwcsa_heroku.TimestampedModel']},
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'num_members_required': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'shift': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gwcsa_heroku.WorkShift']"}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            u'timestampedmodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gwcsa_heroku.TimestampedModel']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['gwcsa_heroku']