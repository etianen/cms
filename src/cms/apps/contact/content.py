"""Content models for the contact form application."""


from django import template
from django.conf import settings
from django.core.mail import send_mass_mail
from django.http import HttpResponseRedirect

from cms.apps.pages import content
from cms.apps.contact.forms import ContactForm


DEFAULT_SUCCESS_MESSAGE = """<p>Thank you for your enquiry. We will be in touch with you shortly.</p>"""


DEFAULT_CONFIRMATION_MESSAGE = """Dear {{name}},

Thank you for your enquiry. We will be in touch with you shortly.

Best wishes,

The %s Team.""" % settings.SITE_NAME 


registered_forms = {}


class FormRegistrationError(Exception):
    
    """Exception raised when something goes wrong with form registration."""


def register_form(form_cls, slug=None):
    """Registers the fiven contact form under the given slug."""
    slug = slug or form_cls.__name__.lower()
    registered_forms[slug] = form_cls
    

def unregister_form(slug):
    """Unregisters the given contact form."""
    try:
        del registered_forms[slug]
    except KeyError:
        raise FormRegistrationError, "No contact form is registered under '%s'." % slug
    
    
def lookup_form(slug):
    """Looks up the contact form associated with the given slug."""
    try:
        return registered_forms[slug]
    except KeyError:
        raise FormRegistrationError, "No contact form is registered under '%s'." % slug
    
    
def form_choices():
    """Returns a sorted list of all form choices."""
    choices = registered_forms.items()
    choices.sort(lambda a, b: cmp(a[1].verbose_name, b[1].verbose_name))
    choices = [(slug, form_cls.verbose_name.capitalize()) for slug, form_cls in choices]
    return choices


DEFAULT_CONTACT_FORM_SLUG = "contact"


register_form(ContactForm, DEFAULT_CONTACT_FORM_SLUG)


class ContactForm(content.Content):
    
    """A standard method of creating contact forms."""
    
    classifier = "utilities"
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/contact-form.png"
    
    form_type = content.ChoiceField(choices=form_choices(),
                                    default=DEFAULT_CONTACT_FORM_SLUG,
                                    required=True,
                                    help_text="The type of form used for this contact page.")
    
    send_to = content.EmailField(required=True,
                                 help_text="The email address that shall be sent messages from this contact form.")
    
    success_message = content.HtmlField(required=True,
                                        default=DEFAULT_SUCCESS_MESSAGE,
                                        help_text="The message that shall be displayed to the user once the form is submitted.")
    
    confirmation_subject = content.CharField("subject",
                                             required=True,
                                             default="%s - Online Enquiry" % settings.SITE_NAME,
                                             help_text="The subject of the confirmation email is sent to the user.")
    
    confirmation_message = content.TextField("message",
                                             required=True,
                                             default=DEFAULT_CONFIRMATION_MESSAGE,
                                             help_text="The confirmation email that is sent to the user.")
    
    def get_fieldsets(self):
        """Returns the fieldsets used to lay out the content form."""
        return (("Page content", {"fields": content.CONTENT_AREA_NAMES + ("success_message",)}),
                ("Form details", {"fields": ("form_type", "send_to",),}),
                ("Confirmation email", {"fields": ("confirmation_subject", "confirmation_message",),}),)
    
    @content.view(r"^$")
    def index(self, request):
        """Renders the contact form."""
        ContactForm = lookup_form(self.form_type)
        # Respond to POST data.
        if request.method == "POST":
            contact_form = ContactForm(request.POST)
            if contact_form.is_valid():
                subject = self.confirmation_subject
                name = contact_form.cleaned_data["name"]
                email = contact_form.cleaned_data["email"]
                sender = "%s <%s>" % (name, email)
                recipient = self.send_to
                messages = []
                # Compile the email to the contact form recipient.
                notification_context = {"name": name,
                                        "email": email,
                                        "contact_form": contact_form}
                notification_message = template.loader.render_to_string("contact/notification.txt", notification_context)
                messages.append((subject, 
                                 notification_message, 
                                 sender, 
                                 [recipient]))
                # Compile the confirmation email.
                confirmation_context = template.RequestContext(request, contact_form.cleaned_data)
                confirmation_email = template.Template(self.confirmation_message)
                confirmation_message = confirmation_email.render(confirmation_context)
                messages.append((subject,
                                 confirmation_message,
                                 recipient,
                                 [sender]))
                # Send both emails.
                send_mass_mail(messages)
                # Redirect the user.
                return HttpResponseRedirect(self.reverse("message_sent"))
        else:    
            contact_form = ContactForm()
        context = {"contact_form": contact_form}
        return self.render_to_response(request, "contact/contact_form.html", context)
    
    @content.view(r"^message-sent/$")
    def message_sent(self, request):
        """Renders a success message to the user."""
        context = {"title": "Message Sent"}
        return self.render_to_response(request, "contact/message_sent.html", context)
        
        
content.register(ContactForm)

