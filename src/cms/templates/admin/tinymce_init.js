/*
    Initializes the TinyMCE editor.
*/


$(function() {
    $("textarea.html").tinymce({
        script_url: "{{CMS_MEDIA_URL}}js/tiny_mce/tiny_mce.js",
        theme: "advanced",
        plugins: "table, advimage, media, inlinepopups, paste",
        paste_auto_cleanup_on_paste: true,
        paste_remove_spans: true,
        paste_remove_styles: true,
        theme_advanced_buttons1: "code,|,formatselect,styleselect,|,bullist,numlist,table,|,bold,italic,|,sub,sup,|,link,unlink,image,media",
        theme_advanced_buttons2: "",
        theme_advanced_buttons3: "",
        width: "700px",
        height: "350px",
        dialog_type: "modal",
        theme_advanced_blockformats: "h2,h3,p",
        external_link_list_url: "{% url tinymce_link_list %}",
        external_image_list_url: "{% url tinymce_image_list %}",
        content_css: "{{TINYMCE_CONTENT_CSS}}",
        extended_valid_elements : "iframe[src|width|height|name|align]",
        convert_urls: false,
        button_tile_map : true,
        entity_encoding: "raw",
        verify_html: false
    })
});

