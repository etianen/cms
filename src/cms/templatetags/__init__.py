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
        raise template.TemplateSyntaxError('{tag_name} tag expects the following format: "{tag_format}"'.format(
            tag_name = token.split_contents()[0],
            tag_format = '" or "'.join(patterns)
        ))
        
    def render(self, context):
        """Renders the PatternNode."""
        kwargs = self.flags.copy()
        for key, value in self.variables.items():
            kwargs[key] = value.resolve(context)
        return self.handler(context, **kwargs)