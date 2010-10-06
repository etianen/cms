"""Extensions to Django's file handling."""


import re

from django.core.files.storage import default_storage


RE_WHITESPACE = re.compile(ur"[\s_]+")
RE_NONALPHA = re.compile(ur"[^a-z0-9\-\.]")


def clean_path_component(path):
    """Clean a component in a filesystem path."""
    path = path.lower()
    path = RE_WHITESPACE.sub(u"-", path)
    path = RE_NONALPHA.sub(u"", path)
    return path
    
    
def get_upload_path(instance, filename):
    """
    Generates the upload path for static media files.
    
    This will attempt to prevent filename mangling by prefixing the filename
    with a folder representing the version of the file that was uploaded.
    It will also attempt to prevent filesystem incompatibilities by sanitizing
    the filename to lowercase, and removing non-alphanumeric characters.
    """
    filename = clean_path_component(filename)
    folder_name = clean_path_component(instance._meta.verbose_name_plural)
    file_version = 1
    while True:
        upload_path = "uploads/%s/%i/%s" % (folder_name, file_version, filename)
        if not default_storage.exists(upload_path):
            return upload_path
        file_version += 1