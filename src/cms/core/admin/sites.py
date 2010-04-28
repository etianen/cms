"""Extensions to the Django admin site."""


from __future__ import with_statement

import functools, itertools

from django import template
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.shortcuts import render_to_response
from django.views.generic.simple import direct_to_template

from cms.core import permalinks
from cms.core.models.managers import publication_manager


class AdminSite(admin.AdminSite):
    
    """The CMS admin site."""
    
    index_template = "admin/dashboard.html"
    
    def __init__(self, *args, **kwargs):
        """Initializes the admin site."""
        super(AdminSite, self).__init__(*args, **kwargs)
        self._link_list_models = set()
    
    def register_link_list(self, model):
        """Registers a model in the admin tinymce link list generator."""
        self._link_list_models.add(model)
        
    def unregister_link_list(self, model):
        """Removes a model from the admin tinymce link list generator."""
        self._link_list_models.remove(model)
    
    # Custom admin views.
    
    def get_urls(self):
        """Generates custom admin URLS."""
        urls = super(AdminSite, self).get_urls()
        custom_urls = patterns("",
                               url(r"^tinymce-init.js$", self.admin_view(direct_to_template), kwargs={"template": "admin/tinymce_init.js", "mimetype": "text/javascript"}, name="tinymce_init"),
                               url(r"^tinymce-link-list.js$", self.admin_view(self.tinymce_link_list), name="tinymce_link_list"),)
        return custom_urls + urls
    
    def admin_view(self, view, *args, **kwargs):
        """Turns off publication management for admin views."""
        view = super(AdminSite, self).admin_view(view, *args, **kwargs)
        @functools.wraps(view)
        def wrapper(*args, **kwargs):
            with publication_manager.select_published(False):
                return view(*args, **kwargs)
        return wrapper
    
    def tinymce_link_list(self, request):
        """Generates the tinymce link list."""
        generators = []
        for model in self._link_list_models:
            generators.append((unicode(obj), permalinks.create(obj)) for obj in model._default_manager.all().iterator())
        links = sorted(itertools.chain(*generators))
        context = {"links": links}
        return render_to_response("admin/tinymce_link_list.js", context, template.RequestContext(request), mimetype="text/javascript")