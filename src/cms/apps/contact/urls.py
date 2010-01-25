"""URLs used by the contact forms application."""


from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("cms.apps.contact.views",
                       url(r"^$", "index", name="index"),
                       url(r"^message-sent/$", "message_sent", name="message_sent"),)

