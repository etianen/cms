"""Core views used by the CMS."""


from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from cms.apps.pages.models import Page


def render_page(request):
    """Dispatches the request to the site pages."""
    try:
        homepage = Page.objects.get_homepage()
    except Page.DoesNotExist:
        raise Http404, "The site does not have a homepage."
    if not homepage.is_published:
        raise Http404, "The site homepage has not been published."
    return homepage.render_to_response(request)


def permalink_redirect(request, content_type_id, object_id):
    """Redirects to the object encoded in the permalink."""
    # Attempt to access the encoded content type.
    try:
        content_type = ContentType.objects.get_for_id(content_type_id)
    except ContentType.DoesNotExist, ex:
        raise Http404, str(ex)
    # Attempt to access the encoded object.   
    try:
        obj = content_type.get_object_for_this_type(pk=object_id)
    except content_type.model_class().DoesNotExist, ex:
        raise Http404, str(ex)
    # Attempt to redirect to the object's absolute URL.
    try:
        redirect_url = obj.get_absolute_url()
    except AttributeError:
        raise Http404, "%s objects do not publish an absolute URL." % content_type.name.title()
    return HttpResponseRedirect(redirect_url)
    
    
def render_template(request, path, base_path=""):
    """
    Serves static template files based on the given path.
    
    If supplied, `base_path` will be prepended onto the path.
    """
    template_name = base_path + path
    if not template_name or template_name.endswith("/"):
        template_name += "base.html"
    try:
        return render_to_response(template_name, {}, template.RequestContext(request))
    except template.TemplateDoesNotExist:
        raise Http404, "The template '%s' does not exist." % template_name
    
    
def tinymce_init(request):
    """Renders the TinyMCE initialization script."""
    context = {"TINYMCE_CONTENT_CSS": settings.TINYMCE_CONTENT_CSS}
    return render_to_response("admin/tinymce_init.js", context, template.RequestContext(request), mimetype="text/javascript")


def reorder_pages(request):
    """Swaps the ordering of two pages."""
    # Get the POST variables.
    page_ids = request.POST.getlist("pages")
    # Get the page objects.
    pages = Page.objects.filter(id__in=page_ids)
    page_0_order = pages[0].order
    page_1_order = pages[1].order
    # Blank their order fields.
    for page in pages:
        page.order = None
        page.save()
    # Swap their order fields.
    pages[0].order = page_1_order
    pages[1].order = page_0_order
    pages[0].save()
    pages[1].save()
    # Send a positive response.
    return HttpResponse("Swapped page '%s' with page '%s'." % (pages[0], pages[1]))
        
