# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Page'
        db.create_table('pages_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_online', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('browser_title', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('meta_keywords', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('meta_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('sitemap_priority', self.gf('django.db.models.fields.FloatField')(default=None, null=True, blank=True)),
            ('sitemap_changefreq', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('robots_index', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('robots_follow', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('robots_archive', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('url_title', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('short_title', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='child_set', null=True, to=orm['pages.Page'])),
            ('left', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('right', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('publication_date', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('expiry_date', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('in_navigation', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
        ))
        db.send_create_signal('pages', ['Page'])

        # Adding unique constraint on 'Page', fields ['parent', 'url_title']
        db.create_unique('pages_page', ['parent_id', 'url_title'])

    def backwards(self, orm):
        # Removing unique constraint on 'Page', fields ['parent', 'url_title']
        db.delete_unique('pages_page', ['parent_id', 'url_title'])

        # Deleting model 'Page'
        db.delete_table('pages_page')

    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'pages.page': {
            'Meta': {'ordering': "('left',)", 'unique_together': "(('parent', 'url_title'),)", 'object_name': 'Page'},
            'browser_title': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'expiry_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_navigation': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_online': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'left': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child_set'", 'null': 'True', 'to': "orm['pages.Page']"}),
            'publication_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'right': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'robots_archive': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'robots_follow': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'robots_index': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'sitemap_changefreq': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'sitemap_priority': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'url_title': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['pages']