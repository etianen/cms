import sys, os
sys.path.append("src")

from cms import VERSION

from setuptools import setup, find_packages


VERSION_STR = ".".join(str(n) for n in VERSION)
        

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
    packages = find_packages("src"),
    include_package_data = True,
    entry_points = {
        "console_scripts": [
            "start_cms_project.py = cms.bin.start_cms_project:main",
        ],
    },
    install_requires = [
        "django",
        "django-optimizations",
        "Pillow",
    ],
    extras_require = {
        "full":  [
            "django-reversion",
            "django-usertools",
            "django-historylinks",
            "django-watson",
            "south",
            "psycopg2",
        ],
    },
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
