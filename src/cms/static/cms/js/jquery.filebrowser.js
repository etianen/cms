/*
    TinyMCE filebrowser implementation.
*/


(function($, tinyMCE, tinyMCEPopup) {
    
    // Define the filebrowser plugin.
    $.filebrowser = {}
    
    // Filebrowser callback for TinyMCE.
    $.filebrowser.createCallback = function(browserURL) {
        return function(field_name, url, type, win) {
            if (browserURL.indexOf("?") < 0) {
                browserURL = browserURL + "?"
            }
            if (type == "image") {
                browserURL = browserURL + '&file__iregex=\x5C.(png|gif|jpg|jpeg)$';
            }
            if (type == "media") {
                browserURL = browserURL + '&file__iregex=\x5C.(swf|flv|m4a|mov|wmv)$';
            }
            tinyMCE.activeEditor.windowManager.open({
                file: browserURL,
                title: "Select file",
                width: 800,
                height: 600,
                resizable: "yes",
                inline: "yes",
                close_previous: "no",
                popup_css: false
            }, {
                window: win,
                input: field_name
            });
            return false;
        }
    }
    
    // Closes the filebrowser and sends the information back to the TinyMCE editor.
    $.filebrowser.complete = function(permalink, title) {
        // Get the important values from TinyMCE.
        var win = tinyMCEPopup.getWindowArg("window");
        // Get the input from the opening window.
        var input = $("#" + tinyMCEPopup.getWindowArg("input"), win.document);
        input.attr("value", permalink);
        // Set the link dialogue values.
        $("#linktitle", win.document).attr("value", title);
        // Set the image dialogue values.
        if (typeof(win.ImageDialog) != "undefined") {
            if (win.ImageDialog.getImageData) {
                win.ImageDialog.getImageData();
            }
            if (win.ImageDialog.showPreviewImage) {
                win.ImageDialog.showPreviewImage(permalink);
            }
        }
        // Close the dialogue.
        tinyMCEPopup.close();
    }
    
    // Initializes the popup file browser.
    $.filebrowser.initBrowser = function() {
        // Make the changelist links clickable and remove the original inline click listener.
        $("div#changelist tr.row1 a, div#changelist tr.row2 a").attr("onclick", null).click(function() {
            var img = $("img", this);
            var title = img.attr("title");
            var permalink = img.attr("cms:permalink");
            $.filebrowser.complete(permalink, title)
            return false;
        });
        // Made the add link flagged for TinyMCE.
        $("a.addlink").attr("href", $("a.addlink").attr("href") + "&_tinymce=1");
    }

}(django.jQuery, tinyMCE, window.tinyMCEPopup));