"""Content models for the contact form application."""


from django.conf import settings

from cms.core import loader
from cms.apps.pages import content


DEFAULT_SUCCESS_MESSAGE = """<p>Thank you for your enquiry. We will be in touch with you shortly.</p>"""


DEFAULT_CONFIRMATION_MESSAGE = """Dear {{name}},

Thank you for your enquiry. We will be in touch with you shortly.

Best wishes,

The %s Team.""" % settings.SITE_NAME 


# Dynamically load contact form choices.

CONTACT_FORMS = tuple((key, loader.load_object(value)) for key, value in settings.CONTACT_FORMS)

CONTACT_FORM_CHOICES = tuple((key, value.verbose_name.capitalize()) for key, value in CONTACT_FORMS)

CONTACT_FORM_CHOICES_DEFAULT = CONTACT_FORM_CHOICES[0][0]

CONTACT_FORMS = dict(CONTACT_FORMS)
    
    
class ContactForm(content.BaseContent):
    
    """A standard method of creating contact forms."""
    
    classifier = "utilities"
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/contact-form.png"
    
    urlconf = "cms.apps.contact.urls"
    
    form_type = content.ChoiceField(choices=CONTACT_FORM_CHOICES,
                                    default=CONTACT_FORM_CHOICES_DEFAULT,
                                    help_text="The type of form used for this contact page.")
    
    send_to = content.EmailField(help_text="The email address that shall be sent messages from this contact form.")
    
    success_message = content.HtmlField(default=DEFAULT_SUCCESS_MESSAGE,
                                        help_text="The message that shall be displayed to the user once the form is submitted.")
    
    confirmation_subject = content.CharField("subject",
                                             default="%s - Online Enquiry" % settings.SITE_NAME,
                                             help_text="The subject of the confirmation email is sent to the user.")
    
    confirmation_message = content.TextField("message",
                                             default=DEFAULT_CONFIRMATION_MESSAGE,
                                             help_text="The confirmation email that is sent to the user.")
    
    def get_fieldsets(self):
        """Returns the fieldsets used to lay out the content form."""
        return super(ContactForm, self).get_fieldsets() + (("Form details", {"fields": ("form_type", "send_to", "success_message"),}),
                                                           ("Confirmation email", {"fields": ("confirmation_subject", "confirmation_message",),}),)