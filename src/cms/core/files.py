"""Extensions to Django's file handling."""


import re, subprocess, os.path

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage, Storage
from django.contrib.staticfiles.storage import StaticFilesStorage

import cms


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


RE_COMPRESSIBLE_FILENAME = re.compile(r"^.+\.(css|js)$")
        
        
class OptimizingStorage(Storage):
    
    """
    A files storage that automatically optimizes and compresses JS and
    CSS files.
    """
    
    def __init__(self, *args, **kwargs):
        """Initializes the OptimizingStorage."""
        storage_cls = kwargs.pop("storage_cls")
        self._inner_storage = storage_cls(*args, **kwargs)
    
    def _open(self, name, mode="rb"):
        """Opens the given file."""
        return self._inner_storage._open(name, mode)

    def _save(self, name, content):
        """Saves the given file."""
        match = RE_COMPRESSIBLE_FILENAME.match(name)
        if match:
            compressor = subprocess.Popen(
                'java -jar "{compressor_path}" --type {type}'.format(
                    compressor_path = os.path.join(os.path.dirname(cms.__file__), "resources", "yuicompressor.jar").replace('"', '\"'),
                    type = match.group(1),
                ),
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE,
                shell = True,
                bufsize = content.size,
            )
            result, _ = compressor.communicate(content.read())
            content = ContentFile(result)
        return self._inner_storage._save(name, content)
    
    def delete(self, name):
        """
        Deletes the specified file from the storage system.
        """
        return self._inner_storage.delete(name)

    def exists(self, name):
        """
        Returns True if a file referened by the given name already exists in the
        storage system, or False if the name is available for a new file.
        """
        return self._inner_storage.exists(name)

    def listdir(self, path):
        """
        Lists the contents of the specified path, returning a 2-tuple of lists;
        the first item being directories, the second item being files.
        """
        return self._inner_storage.listdir(path)

    def size(self, name):
        """
        Returns the total size, in bytes, of the file specified by name.
        """
        return self._inner_storage.size(name)

    def url(self, name):
        """
        Returns an absolute URL where the file's contents can be accessed
        directly by a Web browser.
        """
        return self._inner_storage.url(name)

    def accessed_time(self, name):
        """
        Returns the last accessed time (as datetime object) of the file
        specified by name.
        """
        return self._inner_storage.access_time(name)

    def created_time(self, name):
        """
        Returns the creation time (as datetime object) of the file
        specified by name.
        """
        return self._inner_storage.created_time(name)

    def modified_time(self, name):
        """
        Returns the last modified time (as datetime object) of the file
        specified by name.
        """
        return self._inner_storage.modified_time(name)
        
        
class OptimizingStaticFilesStorage(OptimizingStorage):
    
    """Optimizing static file storage."""
    
    def __init__(self, *args, **kwargs):
        """Initializes the storage."""
        kwargs.setdefault("storage_cls", StaticFilesStorage)
        super(OptimizingStaticFilesStorage, self).__init__(*args, **kwargs)