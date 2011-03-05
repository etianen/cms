"""Template extensions used by the CMS"""


import re
from functools import wraps

from django import template


RE_PATTERN_VARIABLE = re.compile(r"\{(\w+?)\}")
RE_PATTERN_FLAG = re.compile(r"\[(\w+?)\]")

# Cached regular expressions used by pattern tags.
pattern_cache = {}


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
            if not pattern in pattern_cache:
                varnames = set()
                flagnames = set()
                def replace_variables(match):
                    varname = match.group(1)
                    varnames.add(varname)
                    return r"(?P<%s>[\w\.\|:]+?|'.*?'|\".*?\")" % varname
                regex = RE_PATTERN_VARIABLE.sub(replace_variables, pattern)
                def replace_flags(match):
                    flagname = match.group(1)
                    flagnames.add(flagname)
                    return r"(?P<%s>[\S]+?)" % flagname
                regex = RE_PATTERN_FLAG.sub(replace_flags, regex)
                regex = r"^\w+%s$" % (" " + regex).rstrip()
                pattern_cache[pattern] = (re.compile(regex), varnames, flagnames)
            # Attempt to match the token.
            re_pattern, varnames, flagnames = pattern_cache[pattern]
            match = re_pattern.match(token.contents)
            if match:
                variables = {}
                flags = {}
                for key, value in match.groupdict().items():
                    if key in varnames:
                        variables[key] = parser.compile_filter(value)
                    elif key in flagnames:
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


def scoped_inclusion_tag(register, template_name, *patterns):
    """
    A decorator used to defined a more versatile inclusion tag.
    
    The decorated function will be passed the context object and the value of any variables
    parsed from the patterns. The function must return a dictionary of params which will
    be pushed onto the context and used to render the named template.
    
    Once the render has finished, the context will be popped and rendering of the rest of the
    outer template will resume.
    """
    def decorator(func):
        @register.tag
        @wraps(func)
        def compiler(parser, token):
            def handler(context, *args, **kwargs):
                params = func(context, *args, **kwargs)
                context.push()
                context.update(params)
                try:
                    return template.loader.render_to_string(template_name, context)
                finally:
                    context.pop()
            return PatternNode(parser, token, handler, patterns)
        return func
    return decorator