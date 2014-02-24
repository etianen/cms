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
packages, package_data = [], {}

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
cms_dir = 'src/cms'

for dirpath, dirnames, filenames in os.walk(cms_dir):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
    parts = fullsplit(dirpath)[1:]
    package_name = '.'.join(parts)
    if '__init__.py' in filenames:
        packages.append(package_name)
    elif filenames:
        relative_path = []
        while '.'.join(parts) not in packages:
            relative_path.append(parts.pop())
        relative_path.reverse()
        path = os.path.join(*relative_path)
        package_files = package_data.setdefault('.'.join(parts), [])
        package_files.extend([os.path.join(path, f) for f in filenames])


# Create the setup config.

setup(
    name = "etianen-cms",
    version = ".".join(str(n) for n in VERSION),
    description = "A collection of Django extensions that add content-management facilities to Django projects.",
    long_description = open("README.md").read(),
    author = "Dave Hall",
    author_email = "dave@etianen.com",
    url = "http://github.com/etianen/cms",
    zip_safe = False,
    package_dir = {
        "": "src",
    },
    packages = packages,
    package_data = package_data,
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
