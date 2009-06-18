"""Views used by the media application."""


from django import template
from django.shortcuts import render_to_response

from cms.apps.media.models import File, Image


def tinymce_link_list(request):
    """Returns a list of TinyMCE links."""
    files = File.objects.all()
    context = {"files": files}
    return render_to_response("admin/media/file/link_list.js", context, template.RequestContext(request), mimetype="text/javascript")


def tinymce_image_list(request):
    """Returns a list of TinyMCE images."""
    images = Image.objects.all()
    context = {"images": images}
    return render_to_response("admin/media/image/image_list.js", context, template.RequestContext(request), mimetype="text/javascript")
    
    