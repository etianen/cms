"""Template extensions used by the pages application."""


import re

from django import template


class PatternNode(template.Node):
    
    """
    Generic node that matches a given pattern expression.
    
    The following syntax is supported in patterns:
    
    :{variable_name}:
        Interpreted as a variable or filter expression, to be looked up in the
        context.
        
    :[flag]:
        A flag that may or may not be present.
    """
    
    def __init__(self, parser, token, handler, patterns):
        """Initializes the PatternNode."""
        super(PatternNode, self).__init__()
        self.handler = handler
        # Compile the pattern.
        for pattern in patterns:
            variables = {}
            flags = {}
            def replace_variables(match):
                varname = match.group(1)
                variables[varname] = None
                return r"(?P<%s>[\S]+?)" % varname
            regex = re.sub(r"\{(\w+?)\}", replace_variables, pattern)
            def replace_flags(match):
                flagname = match.group(1)
                flags[flagname] = None
                return r"(?P<%s>[\S]+?)" % flagname
            regex = re.sub(r"\[(\w+?)\]", replace_flags, regex)
            regex = r"^\w+%s$" % (" " + regex).rstrip()
            # Attempt to match the token.
            match = re.match(regex, token.contents)
            if match:
                for key, value in match.groupdict().items():
                    if key in variables:
                        variables[key] = parser.compile_filter(value)
                    elif key in flags:
                        flags[key] = value
                    else:
                        raise ValueError, "Unescaped regular expression in pattern: %s" % pattern
                self.variables = variables
                self.flags = flags
                return
        raise template.TemplateSyntaxError, '%s tag expects the following format: "%s"' % (token.split_contents()[0], '" or "'.join(patterns))
        
    def render(self, context):
        """Renders the PatternNode."""
        kwargs = self.flags.copy()
        for key, value in self.variables.items():
            kwargs[key] = value.resolve(context)
        return self.handler(context, **kwargs)

    