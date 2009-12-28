/*
    Initializes the TinyMCE editor.
*/


(function() {
    
    // File browser callback.
    function fileBrowser(input, value, type, win) {
        
    }
    
    // Initialize the editors.
    tinyMCE.init({
        mode: "specific_textareas",
        editor_selector : "html",
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
        content_css: "{{settings.TINYMCE_CONTENT_CSS}}",
        extended_valid_elements : "iframe[src|width|height|name|align]",  // Permit embedded iframes.
        convert_urls: false,
        button_tile_map : true,  // Client-side optimization.
        entity_encoding: "raw",  // Client-side optimization.
        verify_html: false,  // Client-side optimization.
        file_browser_callback: fileBrowser
    });
    
}());

