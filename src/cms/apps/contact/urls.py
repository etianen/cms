"""URLs used by the contact forms application."""


from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("",
                       url(r"^$", "cms.apps.contact.views.index", name="index"),
                       url(r"^message-sent/$", "django.views.generic.simple.direct_to_template", name="message_sent", kwargs={"template": "contact/message_sent.html"}),)