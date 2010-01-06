/*
    Initializes the TinyMCE editor.
*/


(function(tinyMCE) {
    
    // Filebrowser callback.
    function cmsFileBrowser (field_name, url, type, win) {
        
        var browserURL = "{% url admin:media_file_changelist %}?pop=1";
        if (browserURL.indexOf("?") < 0) {
            browserURL = browserURL + "?"
        }
        
        var verboseName = "File";
        if (type == "image") {
            verboseName = "image";
            browserURL = browserURL + '&file__iregex={{settings.FILENAME_IMAGE_PATTERN|escapejs}}';
        }
        if (type == "media") {
            verboseName = "media";
            browserURL = browserURL + '&file__iregex={{settings.FILENAME_MEDIA_PATTERN|escapejs}}';
        }
        
        tinyMCE.activeEditor.windowManager.open({
            file: browserURL,
            title: "Select " + verboseName,
            width: 800,
            height: 600,
            resizable: "yes",
            inline: "yes",
            close_previous: "no",
            popup_css : false
        }, {
            window: win,
            input: field_name
        });
        return false;
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
        content_css: "{{settings.TINYMCE_CONTENT_CSS|escapejs}}",
        extended_valid_elements : "iframe[src|width|height|name|align]",  // Permit embedded iframes.
        convert_urls: false,
        button_tile_map : true,  // Client-side optimization.
        entity_encoding: "raw",  // Client-side optimization.
        verify_html: false,  // Client-side optimization.
        file_browser_callback: cmsFileBrowser
    });
    
}(tinyMCE));