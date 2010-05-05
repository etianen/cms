"""Views used by the contact forms application."""


from django import template
from django.conf import settings
from django.core import mail
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from cms.apps.contact.content import CONTACT_FORMS


def index(request):
    """Renders the contact form."""
    page = request.page
    content = page.content
    ContactForm = CONTACT_FORMS[content.form_type]
    # Respond to POST data.
    if request.method == "POST":
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            cleaned_data = contact_form.cleaned_data
            subject = content.confirmation_subject
            name = contact_form.cleaned_data["name"]
            email = contact_form.cleaned_data["email"]
            sender = "%s <%s>" % (name, email)
            recipient = content.send_to
            messages = []
            # Compile the email to the contact form recipient.
            data = [(field.label, cleaned_data[field.name]) for field in contact_form]
            notification_context = {"name": name,
                                    "email": email,
                                    "data": data}
            notification_message = template.loader.render_to_string("contact/notification.txt", notification_context, template.RequestContext(request))
            messages.append(mail.EmailMessage(subject, 
                                              notification_message, 
                                              settings.DEFAULT_FROM_EMAIL, 
                                              [recipient],
                                              headers={"Reply-To": sender}))
            # Compile the confirmation email.
            confirmation_context = template.RequestContext(request, contact_form.cleaned_data)
            confirmation_email = template.Template(content.confirmation_message)
            confirmation_message = confirmation_email.render(confirmation_context)
            messages.append(mail.EmailMessage(subject,
                                              confirmation_message,
                                              settings.DEFAULT_FROM_EMAIL,
                                              [sender]))
            # Send both emails.
            connection = mail.SMTPConnection()
            connection.send_messages(messages)
            # Redirect the user.
            return redirect(page.reverse("message_sent"))
    else:    
        contact_form = ContactForm()
    context = {"contact_form": contact_form}
    return render_to_response("contact/index.html", context, RequestContext(request))    