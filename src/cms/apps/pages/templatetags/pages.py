"""Template tags used by the CMS."""


import re

from django import template

from cms.apps.pages import permalinks, thumbnails


register = template.Library()


# Define some convenient keywords.


YES = True

NO = False

MAYBE = "maybe"


# HTML tags.


@register.inclusion_tag("first_last.html", takes_context=True)
def first_last(context, first=MAYBE, last=MAYBE):
    """Generates class names to mark items as either first or last in a loop."""
    # Calculate first and last variables.
    if first is MAYBE:
        first = context["forloop"]["first"]
    if last is MAYBE:
        last = context["forloop"]["last"]
    # Generate the context.
    context = {"first": first,
               "last": last}
    return context


@register.inclusion_tag("hyperlink.html", takes_context=True)
def hyperlink(context, title, url):
    """
    Generates a hyperlink referencing the given URL.
    
    The hyperlink will be marked as 'here' if the request path starts with the
    URL.
    """
    request = context["request"]
    context = {"title": title,
               "url": url,
               "is_here": request.path.startswith(url)}
    return context


@register.inclusion_tag("hyperlink.html", takes_context=True)
def hyperlink_exact(context, title, url):
    """
    Generates a hyperlink referencing the given URL.
    
    The hyperlink will be marked as 'here' if the request path exactly equals
    the URL.
    """
    request = context["request"]
    context = {"title": title,
               "url": url,
               "is_here": (request.path == url)}
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
    
    