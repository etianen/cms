"""Management routines for the staff management application."""


from django.contrib.auth import models as auth_application
from django.contrib.auth.models import Group as BaseGroup
from django.db.models.signals import post_syncdb

from cms.staff.models import Group


def create_default_groups(app, created_models, verbosity, **kwargs):
    """Creates the default groups for the staff application."""
    # HACK: Proxy models do not show up in created_models list.
    if BaseGroup in created_models:
        if verbosity >= 2:
            print "Creating administrators group."
        administrators = Group.objects.create_administrators()
        if verbosity >= 2:
            print "Creating editors group."
        editors = Group.objects.create_editors()
        
        
post_syncdb.connect(create_default_groups, auth_application)

