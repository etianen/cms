"""Template tags used by the CMS."""


import re, urllib

from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.forms.util import flatatt
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from cms.apps.pages import permalinks, thumbnails
from cms.apps.pages.models import Page


register = template.Library()


# HTML processing.


RE_ANCHOR = re.compile(r"""<a.*?\shref=["'](.+?)["'].*?>""", re.IGNORECASE)

RE_IMG = re.compile(r"<img(.+?)/>", re.IGNORECASE)

RE_ATTR = re.compile(r"""\s(\w+)=["']([^"']+)["']""", re.IGNORECASE)


@register.filter
@stringfilter
def html(text):
    """
    Processes HTML text.
    
    The text is checked for permalinks embedded in <a> tags, expanding the
    permalinks to their referenced URL.
    """
    if not text:
        return ""
    # Process permalinks.
    offset = 0
    for match in RE_ANCHOR.finditer(text):
        href = match.group(1)
        try:
            obj = permalinks.resolve(href)
        except permalinks.PermalinkError:
            continue
        except ObjectDoesNotExist:
            continue
        new_href = obj.get_absolute_url()
        start = match.start(1)
        end = match.end(1)
        text = u"".join((text[:start+offset], new_href, text[end+offset:]))
        offset += len(new_href) - len(href)
    # Process thumbnails.
    offset = 0
    for match in RE_IMG.finditer(text):
        attrs = match.group(1)
        attr_dict = dict(RE_ATTR.findall(attrs))
        try:
            src = attr_dict["src"]
            width = int(attr_dict["width"])
            height = int(attr_dict["height"])
        except KeyError:
            continue
        except ValueError:
            continue
        try:
            obj = permalinks.resolve(src)
        except ObjectDoesNotExist:
            continue
        thumbnail = thumbnails.resize(obj.file, width, height)
        attr_dict["src"] = thumbnail.url
        attr_dict["width"] = thumbnail.width
        attr_dict["height"] = thumbnail.height
        new_attrs = flatatt(attr_dict)
        start = match.start(1)
        end = match.end(1)
        text = u"".join((text[:start+offset], new_attrs, text[end+offset:]))
        offset += len(new_attrs) - len(attrs)
    return mark_safe(text)

    
# Page linking.


@register.simple_tag
def page_url(page, view_func="index"):
    """Renders the URL of the given view func in the given page."""
    if isinstance(page, int):
        try:
            page = Page.objects.get(id=page)
        except Page.DoesNotExist:
            return "#"
    return page.content.reverse(view_func)


# Pagination.


@register.inclusion_tag("pagination.html", takes_context=True)
def pagination(context, page):
    """Generates pagination for the given page."""
    request = context["request"]
    paginator = page.paginator
    # Generate the context.
    context = {"request": request,
               "count": paginator.count,
               "num_pages": paginator.num_pages,
               "page_range": paginator.page_range,
               "has_next": page.has_next(),
               "has_previous": page.has_previous(),
               "has_other_pages": page.has_other_pages(),
               "page_number": page.number,
               "next_page_number":page.next_page_number(),
               "previous_page_number": page.previous_page_number(),
               "start_index": page.start_index(),
               "end_index": page.end_index()}
    return context


@register.inclusion_tag("pagination_url.html", takes_context=True)
def pagination_url(context, page_number, pagination_key=None):
    """Generates a link to the given page number in the pagination."""
    request = context["request"]
    pagination_key = pagination_key or settings.PAGINATION_KEY
    get_params = request.GET.copy()
    get_params[pagination_key] = page_number
    query_string = urllib.urlencode(get_params)
    url = request.path + "?" + query_string
    context = {"url": url}
    return context


# HTML tags.


@register.inclusion_tag("mark_here.html", takes_context=True)
def mark_here(context, url=None):
    """
    Generates a class name to mark a URL as being at the current request path.
    
    If supplied with a URL, then the class name will be generated if the request
    path starts with the URL.  If not supplied with a URL, then the class name
    will always be generated.
    """
    request = context["request"]
    if url is None:
        is_here = True
    else:
        is_here = request.path.startswith(url)
    context = {"is_here": is_here}
    return context


@register.inclusion_tag("mark_here.html", takes_context=True)
def mark_here_exact(context, url=None):
    """
    Generates a class name to mark a URL as being *exactly* at the current
    request path.
    
    If supplied with a URL, then the class name will be generated if the request
    path exactly equals the URL.  If not supplied with a URL, then the class
    name will always be generated.
    """
    request = context["request"]
    if url is None:
        is_here = True
    else:
        is_here = request.path == url
    context = {"is_here": is_here}
    return context


@register.inclusion_tag("mark_first.html", takes_context=True)
def mark_first(context):
    """
    Generates a class name to mark items as first in a loop.
    
    If used in a for loop, then the class name will only be generated on the
    first iteration.  If used outside of a loop, then the class name will
    always be generated.
    """
    try:
        first = context["forloop"]["first"]
    except KeyError:
        first = True
    context = {"first": first}
    return context


@register.inclusion_tag("mark_last.html", takes_context=True)
def mark_last(context):
    """
    Generates a class name to mark items as last in a loop.
    
    If used in a for loop, then the class name will only be generated on the
    last iteration.  If used outside of a loop, then the class name will
    always be generated.
    """
    try:
        last = context["forloop"]["last"]
    except KeyError:
        last = True
    context = {"last": last}
    return context


# Thumbnail tags.


RE_THUMBNAIL = re.compile(r"^(\w+)\W+([\w\.]+)\W+(\d+)\W+(\d+)$")

RE_THUMBNAIL_ALIAS = re.compile(RE_THUMBNAIL.pattern[:-1] + r"\W+as\W+(\w+)$") 


class ThumbnailNode(template.Node):
    
    """Renders the thumbnail tag."""
    
    def __init__(self, token, method):
        """Initializes the ThumbnailNode."""
        # Parse the token.
        match = RE_THUMBNAIL_ALIAS.match(token.contents)
        if match:
            tag_name, image, width, height, alias = match.groups()
        else:
            match = RE_THUMBNAIL.match(token.contents)
            if match:
                tag_name, image, width, height = match.groups()
                alias = None
            else:
                bits = token.split_contents()
                raise template.TemplateSyntaxError, "Invalid syntax for %s tag." % bits[0]
        # Store the result of the parse.
        self.image = template.Variable(image)
        self.width = int(width)
        self.height = int(height)
        self.alias = alias
        self.method = method
        
    def render(self, context):
        """Renders the thumbnail."""
        image = self.image.resolve(context)
        thumbnail = thumbnails.generate(image, self.width, self.height, self.method)
        # Set an alias, if specified.
        if self.alias:
            context[self.alias] = thumbnail
            return ""
        # Generate the image tag.
        return '<img src="%s" width="%s" height="%s" alt=""/>' % (thumbnail.url, thumbnail.width, thumbnail.height)


@register.tag
def thumbnail(parser, token):
    """
    Generates a thumbnail of the given image, preserving aspect ratio.
    
    This has the syntax:
    
        {% thumbnail image width height %}
        
    The output will be a HTML image tag.
    
    Alternatively, you can specify an alias for the image as follows:
    
        {% thumbnail image width height as alias %}
        
    This will put an thumbnail variable into the context under the given name.
    The thumbnail variable will be of type ImageFile, allowing its url, width
    and height to be accessed.
    """
    return ThumbnailNode(token, thumbnails.THUMBNAIL)
    
    
@register.tag
def resized_thumbnail(parser, token):
    """
    Generates a resized thumbnail of the given image, ignoring aspect ratio.
    
    See the 'thumbnail' tag for appropriate syntax.
    """
    return ThumbnailNode(token, thumbnails.RESIZE)


@register.tag
def cropped_thumbnail(parser, token):
    """
    Generates a cropped thumbnail of the given image, preserving aspect ratio.
    
    See the 'thumbnail' tag for appropriate syntax.
    """
    return ThumbnailNode(token, thumbnails.CROP)


# Permalink tags.


@register.filter
def permalink(obj):
    """Generates a permalink for the given object."""
    return permalinks.create(obj)


# Generate template tags.


class RepeatNode(template.Node):
    
    """A node that repeatedly renders its content."""
    
    def __init__(self, count, nodelist):
        """Initializes the RepeatNode."""
        self.count = count
        self.nodelist = nodelist
        
    def render(self, context):
        """Renders the node."""
        count = self.count
        nodelist = self.nodelist
        result = []
        if "forloop" in context:
            parentloop = context["forloop"]
        else:
            parentloop = {}
        loop_attrs = {"parentloop": parentloop}
        context.push()
        context["forloop"] = loop_attrs
        try:
            for index in range(count):
                # Update forloop attrs.
                loop_attrs["counter0"] = index
                loop_attrs["counter"] = index + 1
                loop_attrs["revcounter"] = count - index
                loop_attrs["revcounter0"] = count - index - 1
                loop_attrs["first"] = (index == 0)
                loop_attrs["last"] = (index == count - 1)
                result.append(nodelist.render(context))
            return u"".join(result)
        finally:
            context.pop()


RE_REPEAT_TAG = re.compile(r"^\w+\W+(\d+)$")


@register.tag
def repeat(parser, token):
    """Generates a range from zero to the given endpoint."""
    result = RE_REPEAT_TAG.match(token.contents)
    if result:
        count = int(result.group(1))
        nodelist = parser.parse(("endrepeat",))
        parser.delete_first_token()
        return RepeatNode(count, nodelist)
    else:
        raise template.TemplateSyntaxError, "Invalid syntax for repeat tag."
    
    