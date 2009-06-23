"""Some HTML utility functions."""


import re


RE_PARAGRAPH = re.compile(r"<p[^>]*>", re.IGNORECASE)


def first_paragraph(text):
    """
    Returns the contents of the first paragraph of the given text.
    
    If the text does not have any paragraphs, and empty string is returned.
    """
    try:
        return RE_PARAGRAPH.split(text)[1].split("</p>")[0]
    except IndexError:
        return ""
    
    