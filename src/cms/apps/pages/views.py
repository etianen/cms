"""Core views used by the CMS."""


from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import redirect

from cms.apps.pages.models import Page


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
    return redirect(redirect_url)
        
        
def handler404(request):
    """Renders a pretty error page."""
    page = Page.objects.get_by_path(request.path)
    context = {"title": "Page Not Found"}
    response = page.content.render_to_response(request, "404.html", context)
    response.status_code = 404
    return response
        

def handler500(request):
    """Renders a pretty error page."""
    page = Page.objects.get_by_path(request.path)
    context = {"title": "Server Error"}
    response = page.content.render_to_response(request, "500.html", context)
    response.status_code = 500
    return response

