CMS Changelog
=============


2.6.5 - 06/08/2014
------------------

* Fixing issues with TinyMCE popups in Django 1.6.


2.6.4 - 28/07/2014
------------------

* Django 1.6.x compatibility.
* Improved start_cms_project.py script with configuration installation root.
* Improved setup.py to work better with pip, and updated installation instructions to use pip as the default installation method.


2.6.3 - 20/11/2013
------------------

*   Added ManyToMany fields for page content models.
*   Enabling WYSIWYG editors in inline related models.
*   Fixing hardcoded template path.


2.6.1 - 01/07/2012
------------------

*   Migrations for all built-in apps.
*   Offline and unindexable models no longer show up in search results.


2.6 - 06/06/2012
----------------

*   Built-in news feed app.
*   Optional integration of django-watson via externals loader.
*   Historylinks delegated to separate app, accessible via externals loader.
*   Simplification of page loading logic.
*   Integration with new Django 1.4 features.
*   Using MPTT implementation to finally fix page publication settings.
*   New management command - start_cms_project.
*   Using standard Django admin site for better integration with 3rd party apps.  


2.5 - 08/02/2012
----------------

*   Adding in permalink to file admin.
*   FileRefField and ImageRefField now use an admin related lookup field.
*   File folders changed to M2M labels.
*   Removing timestamps from many models. Likewise removing AuditBase class.


2.4.1 - 20/10/2011
------------------

*   Content-specific permissions.
*   Added in cached template loader.
*   Static file compression.
*   Added in multi-site page backend support.
*   Integration with django-optimizations.


2.4 - 15/06/2011
----------------

*   General improvements based on new Django 1.3 APIs.
*   Admin performance improvements, notably asynchronous sitemap loader.
*   Thumbnailing performance and rendering enhancements.
*   New historylinks application for tracking old content URLs.
*   Integration of custom fields with South.
*   Better example_project environment.
*   Added in table locks to support more reliable page movement.
*   Adding in support for running CMS-powered sites from a sub-URL via SCRIPT_NAME.
*   Adding in default favicon handling redirect.
*   Added in support for different page backends.
*   Switched to using separate database model for page content, rather than serialized XML (backwards incompatible).


2.3.2 - 21/03/2010
------------------

*   Compatibility fix for Django 1.2.5.
*   Better file upload permission handling.
*   WSIWYG tweaks.


2.3.1 - 16/09/2010
------------------

*   Added advanced permissions to user admin page.
*   Added command to generate default admin groups.
*   Added cache for admin sitemap to greatly improve load times.
*   Improved thumbnailing efficiency using an in-memory size cache.
*   Fixed inline image upload problem in Chrome.
*   Fixed inline image upload problem in IE7.
*   Upgraded TinyMCE to 3.3.9.
*   Fixed IE7 rendering of dashboard sitemap.


2.3 - 09/08/2010
----------------

*   Upgraded TinyMCE to 3.3.7.
*   Added CSRF protection to admin sitemap.
*   Django 1.2 compatibility.


2.2 - 05/05/2010
----------------

*   Email other users from within admin.
*   WYSIWYG editors are now resizeable.
*   Added 'using' clause to pagination tag.
*   Improved scalability of pages content framework.
*   Added author to CMS admin 'last modified' column.
*   Created a CMS 'core' application that contains all base functionality.
*   Merged 'staff' application with 'core' application.
*   Greatly improved efficiency of thumbnail generation routines.
*   Upgraded jQuery to version 1.4.2.
*   Upgraded TinyMCE to version 3.3.4.
*   Several tiny bug fixes.


2.1 - 01/02/2010
----------------

The main purpose of this release was to add in a filebrowser for the TinyMCE
editor. Numerous other improvements and bugfixes made it into the release too.
This was also the change for a refactoring of the applications used by the CMS,
in preparation for a potential open-source release later this year.

*   Added WYSIWYG file browser.
*   Contact form module now adds appropriate reply-to headers for notification emails.
*   More efficient thumbnail expansion in template rendering.
*   More efficient permalink expansion in template rendering.
*   More efficient page dispatch mechanism.
*   Removed keywords field from File model.
*   Removed notes field from File model.
*   Remove size field from File model.
*   Upgraded TinyMCE editor.
*   Upgraded jQuery to version 1.4.
*   More accessible and faster-loading admin sitemap.
*   Removed ability to link to pages using permalinks in HTML content.
*   Added many more unit tests to the framework.
*   Framework refactoring and several tiny bug fixes.