"""Form rendering framework."""


from django import forms, template

from cms.apps.pages.templatetags import Library


register = Library()


@register.body_tag
def form(context, nodelist, form, method="get", action=""):
    """
    Renders the given form.
    
    If the form has a 'template' property, then that template will be used.
    Else, the 'forms/form.html' template will be used.
    """
    context.push()
    try:
        context["form"] = form
        context["form_method"] = method
        context["form_action"] = action
        context["form_body"] = nodelist.render(context)
        form_template = getattr(form, "template", "forms/form.html")
        return template.loader.render_to_string(form_template, context)
    finally:
        context.pop()
        
    
@register.context_tag
def field(context, field):
    """
    Renders the given form field.
    
    If the form has a 'field_template' property, then that template will be
    used.  Else, the 'forms/field.html' template will be used.
    
    If the field is a checkbox, the then 'checkbox_template' property
    will be used, falling back to the 'forms/checkbox.html' template.
    """
    form = context["form"]
    context.push()
    try:
        context["field"] = field
        context["errors"] = field.errors
        context["required"] = field.field.required
        if isinstance(field.field.widget, forms.CheckboxInput):
            field_template = getattr(form, "checkbox_template", "forms/checkbox.html")
        else:
            field_template = getattr(form, "field_template", "forms/field.html")
        return template.loader.render_to_string(field_template, context)
    finally:
        context.pop()
        
        
@register.context_tag
def submit(context, value="Submit"):
    """
    Renders a submit button.
    
    If the form has a 'submit_template' property, then that template will be
    used.  Else, the 'forms/submit.html' template will be used.
    """
    form = context["form"]
    context.push()
    try:
        context["submit_value"] = value
        submit_template = getattr(form, "submit_template", "forms/submit.html")
        return template.loader.render_to_string(submit_template, context)
    finally:
        context.pop()
        
        