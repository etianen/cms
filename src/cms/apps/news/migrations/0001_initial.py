# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'NewsFeed'
        db.create_table('news_newsfeed', (
            ('page', self.gf('django.db.models.fields.related.OneToOneField')(related_name='+', unique=True, primary_key=True, to=orm['pages.Page'])),
            ('content_primary', self.gf('cms.models.fields.HtmlField')(blank=True)),
            ('per_page', self.gf('django.db.models.fields.IntegerField')(default=5, null=True, blank=True)),
        ))
        db.send_create_signal('news', ['NewsFeed'])

        # Adding model 'Category'
        db.create_table('news_category', (
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
            ('content_primary', self.gf('cms.models.fields.HtmlField')(blank=True)),
        ))
        db.send_create_signal('news', ['Category'])

        # Adding unique constraint on 'Category', fields ['url_title']
        db.create_unique('news_category', ['url_title'])

        # Adding model 'Article'
        db.create_table('news_article', (
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
            ('news_feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['news.NewsFeed'])),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now, db_index=True)),
            ('image', self.gf('cms.apps.media.models.ImageRefField')(blank=True, related_name='+', null=True, on_delete=models.PROTECT, to=orm['media.File'])),
            ('content', self.gf('cms.models.fields.HtmlField')(blank=True)),
            ('summary', self.gf('cms.models.fields.HtmlField')(blank=True)),
        ))
        db.send_create_signal('news', ['Article'])

        # Adding unique constraint on 'Article', fields ['news_feed', 'date', 'url_title']
        db.create_unique('news_article', ['news_feed_id', 'date', 'url_title'])

        # Adding M2M table for field categories on 'Article'
        db.create_table('news_article_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm['news.article'], null=False)),
            ('category', models.ForeignKey(orm['news.category'], null=False))
        ))
        db.create_unique('news_article_categories', ['article_id', 'category_id'])

        # Adding M2M table for field authors on 'Article'
        db.create_table('news_article_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm['news.article'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('news_article_authors', ['article_id', 'user_id'])

    def backwards(self, orm):
        # Removing unique constraint on 'Article', fields ['news_feed', 'date', 'url_title']
        db.delete_unique('news_article', ['news_feed_id', 'date', 'url_title'])

        # Removing unique constraint on 'Category', fields ['url_title']
        db.delete_unique('news_category', ['url_title'])

        # Deleting model 'NewsFeed'
        db.delete_table('news_newsfeed')

        # Deleting model 'Category'
        db.delete_table('news_category')

        # Deleting model 'Article'
        db.delete_table('news_article')

        # Removing M2M table for field categories on 'Article'
        db.delete_table('news_article_categories')

        # Removing M2M table for field authors on 'Article'
        db.delete_table('news_article_authors')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
        },
        'news.article': {
            'Meta': {'ordering': "('-date',)", 'unique_together': "(('news_feed', 'date', 'url_title'),)", 'object_name': 'Article'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'browser_title': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['news.Category']", 'symmetrical': 'False', 'blank': 'True'}),
            'content': ('cms.models.fields.HtmlField', [], {'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('cms.apps.media.models.ImageRefField', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': "orm['media.File']"}),
            'is_online': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'news_feed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['news.NewsFeed']"}),
            'robots_archive': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'robots_follow': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'robots_index': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'sitemap_changefreq': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'sitemap_priority': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'summary': ('cms.models.fields.HtmlField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'url_title': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'news.category': {
            'Meta': {'ordering': "('title',)", 'unique_together': "(('url_title',),)", 'object_name': 'Category'},
            'browser_title': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'content_primary': ('cms.models.fields.HtmlField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_online': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'robots_archive': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'robots_follow': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'robots_index': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'sitemap_changefreq': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'sitemap_priority': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'url_title': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'news.newsfeed': {
            'Meta': {'object_name': 'NewsFeed'},
            'content_primary': ('cms.models.fields.HtmlField', [], {'blank': 'True'}),
            'page': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'+'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['pages.Page']"}),
            'per_page': ('django.db.models.fields.IntegerField', [], {'default': '5', 'null': 'True', 'blank': 'True'})
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

    complete_apps = ['news']