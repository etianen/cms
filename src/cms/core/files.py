"""Extensions to Django's file handling."""


import re

from django.core.files.storage import default_storage


RE_WHITESPACE = re.compile("\s+")
    
    
def get_upload_path(instance, filename):
    """
    Generates the upload path for static media files.
    
    This will attempt to prevent filename mangling by prefixing the filename
    with a folder representing the version of the file that was uploaded.
    """
    filename = RE_WHITESPACE.sub("-", filename)
    folder_name = instance._meta.verbose_name_plural.replace(" ", "-")
    file_version = 1
    while True:
        upload_path = "uploads/%s/%i/%s" % (folder_name, file_version, filename)
        if not default_storage.exists(upload_path):
            return upload_path
        file_version += 1