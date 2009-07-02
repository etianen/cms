"""Template extensions used by the pages application."""


import re

from django.template import Library as LibraryBase, Variable, Node, TemplateSyntaxError


class ContextNode(Node):
    
    """A node for a context tag."""
    
    def __init__(self, func, args):
        """Initializes the ContextNode."""
        self.func = func
        self.args = args
        
    def render(self, context):
        """Renders the node."""
        args = [arg.resolve(context) for arg in self.args]
        return self.func(context, *args)
    
    
class BodyNode(Node):
    
    """A node for a body tag."""
    
    def __init__(self, func, args, nodelist):
        """Initializes the BodyNode."""
        self.func = func
        self.args = args
        self.nodelist = nodelist
        
    def render(self, context):
        """Renders the node."""
        args = [arg.resolve(context) for arg in self.args]
        return self.func(context, self.nodelist, *args)


class PatternNode(Node):
    
    """A node for a pattern tag."""
    
    def __init__(self, func, kwargs):
        """Initializes the PatternNode."""
        self.func = func
        self.kwargs = kwargs
        
    def render(self, context):
        """Renders the node."""
        kwargs = dict([(key, value.resolve(context)) for key, value in self.kwargs.items()])
        return self.func(context, **kwargs)


class Library(LibraryBase):
    
    """An extended Django template library."""
    
    def context_tag(self, func):
        """
        Decorator for functions to make them a template tag.
        
        Works like the simple_tag decorator, but automatically adds the context
        to the to function.  The first argument of the function must be
        'context'.
        """
        def compiler(parser, token):
            contents = token.split_contents()
            args = [Variable(args) for args in contents[1:]]
            return ContextNode(func, args)
        self.tag(func.__name__, compiler)
        return func
            
    def body_tag(self, func):
        """
        Decorator for functions to make them a template tag.
        
        Works like a context tag, but a second required argument called
        'nodelist' is also passed to the function.  The end tag for the function
        must be the original tag name with 'end' prepended.
        """ 
        def compiler(parser, token):
            contents = token.split_contents()
            tag_name = contents[0]
            end_tag_name = "end" + tag_name
            nodelist = parser.parse((end_tag_name,))
            parser.delete_first_token()
            args = [Variable(args) for args in contents[1:]]
            return BodyNode(func, args, nodelist)
        self.tag(func.__name__, compiler)
        return func
    
    def pattern_tag(self, *patterns):
        """
        A tag that obtains its arguments as the basis of one or more pattern
        constructs.
        
        A pattern has the syntax "{placeholder1} filer text {placeholder2}".
        These placeholders will be provided to the function in the form of
        keyword arguments. The function will also receive the template context
        as the first non-keyword argument.
        
        These patterns will be matched in the order given, so more complete
        patterns should be listed first.
        """
        def decorator(func):
            def compiler(parser, token):
                for pattern in patterns:
                    regex = r"^\w+ %s$" % re.sub(r"\{(\w+?)\}", r"(?P<\1>'[^']*'|\"[^\"]*\"|[\w\.]+?)", pattern)
                    match = re.match(regex, token.contents)
                    if match:
                        kwargs = dict([(key, Variable(value)) for key, value in match.groupdict().items()])
                        return PatternNode(func, kwargs)
                raise TemplateSyntaxError, '%s tag expects the following format: "%s"' % (func.__name__, "' or '".join(patterns))
            self.tag(func.__name__, compiler)
            return func
        return decorator
    
    