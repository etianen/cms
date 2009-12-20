"""Content models for the contact form application."""


from django import template
from django.conf import settings
from django.core.mail import send_mass_mail
from django.shortcuts import redirect

from cms.apps.pages import content
from cms.apps.utils import loader


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
    
    
DefaultContent = content.get_default_content()
    
    
class ContactForm(DefaultContent):
    
    """A standard method of creating contact forms."""
    
    classifier = "utilities"
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/contact-form.png"
    
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
    
    @content.view(r"^$")
    def index(self, request):
        """Renders the contact form."""
        ContactForm = CONTACT_FORMS[self.form_type]
        # Respond to POST data.
        if request.method == "POST":
            contact_form = ContactForm(request.POST)
            if contact_form.is_valid():
                cleaned_data = contact_form.cleaned_data
                subject = self.confirmation_subject
                name = contact_form.cleaned_data["name"]
                email = contact_form.cleaned_data["email"]
                sender = "%s <%s>" % (name, email)
                recipient = self.send_to
                messages = []
                # Compile the email to the contact form recipient.
                data = [(field.label, cleaned_data[field.name]) for field in contact_form]
                notification_context = {"name": name,
                                        "email": email,
                                        "data": data}
                notification_message = template.loader.render_to_string("contact/notification.txt", notification_context, template.RequestContext(request))
                messages.append((subject, 
                                 notification_message, 
                                 settings.DEFAULT_FROM_EMAIL, 
                                 [recipient]))
                # Compile the confirmation email.
                confirmation_context = template.RequestContext(request, contact_form.cleaned_data)
                confirmation_email = template.Template(self.confirmation_message)
                confirmation_message = confirmation_email.render(confirmation_context)
                messages.append((subject,
                                 confirmation_message,
                                 settings.DEFAULT_FROM_EMAIL,
                                 [sender]))
                # Send both emails.
                send_mass_mail(messages)
                # Redirect the user.
                return redirect(self.reverse("message_sent"))
        else:    
            contact_form = ContactForm()
        context = {"contact_form": contact_form}
        return self.render_to_response(request, "contact/contact_form.html", context)
    
    @content.view(r"^message-sent/$")
    def message_sent(self, request):
        """Renders a success message to the user."""
        context = {"title": "Message Sent"}
        return self.render_to_response(request, "contact/message_sent.html", context)
        
        