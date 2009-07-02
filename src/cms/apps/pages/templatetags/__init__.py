"""Template extensions used by the pages application."""


from django.template import Library as LibraryBase, Variable, Node


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
    
    