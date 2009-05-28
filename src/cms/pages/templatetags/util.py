"""Some useful template tags."""


import re

from django import template
from django.template.defaulttags import ForNode


register = template.Library()


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
        
        