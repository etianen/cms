{% load url from future %}
/*
    Initializes the TinyMCE editor.
*/

(function($, tinyMCE) {
    
    // Initialize the editors.
    tinyMCE.init({
        mode: "specific_textareas",
        editor_selector : "html",
        theme: "advanced",
        plugins: "table, advimage, inlinepopups, paste",
        paste_auto_cleanup_on_paste: true,
        paste_remove_spans: true,
        paste_remove_styles: true,
        theme_advanced_buttons1: "code,|,formatselect,styleselect,|,bullist,numlist,table,hr,|,bold,italic,|,sub,sup,|,link,unlink,image",
        theme_advanced_buttons2: "",
        theme_advanced_buttons3: "",
        theme_advanced_resizing: true,
        theme_advanced_path: false,
        theme_advanced_statusbar_location: "bottom",
        width: "700px",
        height: "350px",
        dialog_type: "modal",
        external_link_list_url: "{% url 'admin:tinymce_link_list' %}",
        theme_advanced_blockformats: "h2,h3,p",
        content_css: "{{STATIC_URL|escapejs}}site/css/content.css",
        extended_valid_elements : "iframe[src|width|height|name|align]",  // Permit embedded iframes.
        convert_urls: false,
        file_browser_callback: $.filebrowser.createCallback("{% url 'admin:media_file_changelist' %}?pop=1"),
        accessibility_warnings: false
    });
    
}(django.jQuery, tinyMCE));