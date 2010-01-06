/*
    TinyMCE filebrowser implementation.
*/


$(function() {
    
    // Get the important values from TinyMCE.
    var win = tinyMCEPopup.getWindowArg("window");
    var inputId = tinyMCEPopup.getWindowArg("input");
    
    // Get the input from the opening window.
    var input = $("#" + inputId, win.document);
    
    // Make the links clickable.
    $("div#changelist tr.row1 a, div#changelist tr.row2 a").click(function() {
        input.attr("value", "FOO");
        tinyMCEPopup.close();
        return false;
    });
    
    
    
    /*
    // are we an image browser
    if (typeof(win.ImageDialog) != "undefined") {
        // we are, so update image dimensions...
        if (win.ImageDialog.getImageData)
            win.ImageDialog.getImageData();

        // ... and preview if necessary
        if (win.ImageDialog.showPreviewImage)
            win.ImageDialog.showPreviewImage(URL);
    }
    */
    
    
});

