/*
    TinyMCE filebrowser implementation.
*/


(function($, tinyMCE) {
    
    // Get the important values from TinyMCE.
    var win = tinyMCEPopup.getWindowArg("window");
    var inputId = tinyMCEPopup.getWindowArg("input");
    // Get the input from the opening window.
    var input = $("#" + inputId, win.document);
    
    // Define the filebrowser plugin.
    $.filebrowser = {}
    
    // Closes the filebrowser and sends the information back to the TinyMCE
    // editor.
    $.filebrowser.complete = function(permalink, title) {
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
            $("#alt", win.document).attr("value", title);
            $("#title", win.document).attr("value", title);
        }
        // Close the dialogue.
        tinyMCEPopup.close();
        return false;
    }
    
    // Initializes the popup file browser.
    $.filebrowser.initBrowser = function() {
        // Make the changelist links clickable and remove the original inline click listener.
        $("div#changelist tr.row1 a, div#changelist tr.row2 a").attr("onclick", null).click(function() {
            var img = $("img", this);
            var title = img.attr("title");
            var permalink = img.attr("cms:permalink");
            $.filebrowser.complete(permalink, title)
        });
        // Make the add link clickable.
        $("a.addlink").click(function() {
            tinyMCE.activeEditor.windowManager.open({
                file: $(this).attr("href") + "&_tinymce=1",
                title: "Add file",
                width: 760,
                height: 400,
                resizable: "yes",
                inline: "yes",
                close_previous: "no",
                popup_css: false,
            }, {
                window: win,
                input: inputId
            });
            tinyMCEPopup.close();
            return false;
        });
    }

}(jQuery, tinyMCE));