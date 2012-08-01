import sys, os
sys.path.append("src")
from cms import VERSION

from distutils.core import setup

VERSION_STR = ".".join(str(n) for n in VERSION)


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
cms_dir = 'src/cms'

for dirpath, dirnames, filenames in os.walk(cms_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)[1:]))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])
        

# Create the setup config.
setup(
    name = "etianen-cms",
    version = ".".join(str(n) for n in VERSION),
    description = "A collection of Django extensions that add content-management facilities to Django projects.",
    long_description = open("README.md").read(),
    author = "Dave Hall",
    author_email = "dave@etianen.com",
    url = "http://github.com/etianen/cms",
    download_url = "http://github.com/downloads/etianen/cms/etianen-cms-{version_str}.tar.gz".format(version_str=VERSION_STR),
    zip_safe = False,
    package_dir = {
        "": "src",
    },
    packages = packages,
    data_files = data_files,
    scripts = ['src/cms/bin/start_cms_project.py'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
)