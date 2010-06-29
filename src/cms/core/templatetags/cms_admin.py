"""Template tags used by the CMS admin."""


from django import template

from cms.core import loader


register = template.Library()


@register.tag
def dynamic_tag(parser, token):
    """
    Loads in a template tag with the given name.
    
    This is useful when a standard {% load %} tag cannot be used, as the named
    tag library exists in a Django app that hasn't been used in the project.
    """
    contents = token.split_contents()
    tag_name = contents[1]
    rest = " ".join(contents[2:])
    tag_ref = loader.load_object(tag_name)
    token_contents = tag_ref.__name__ + (rest and " %s" % rest or "")
    return tag_ref(parser, template.Token(template.TOKEN_BLOCK, token_contents))