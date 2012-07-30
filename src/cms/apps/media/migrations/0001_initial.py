# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Label'
        db.create_table('media_label', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('media', ['Label'])

        # Adding model 'File'
        db.create_table('media_file', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=250)),
        ))
        db.send_create_signal('media', ['File'])

        # Adding M2M table for field labels on 'File'
        db.create_table('media_file_labels', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('file', models.ForeignKey(orm['media.file'], null=False)),
            ('label', models.ForeignKey(orm['media.label'], null=False))
        ))
        db.create_unique('media_file_labels', ['file_id', 'label_id'])

    def backwards(self, orm):
        # Deleting model 'Label'
        db.delete_table('media_label')

        # Deleting model 'File'
        db.delete_table('media_file')

        # Removing M2M table for field labels on 'File'
        db.delete_table('media_file_labels')

    models = {
        'media.file': {
            'Meta': {'ordering': "('title',)", 'object_name': 'File'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'labels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['media.Label']", 'symmetrical': 'False', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'media.label': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Label'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['media']