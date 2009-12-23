/*
    Dynamic content for the CMS dashboard.
*/


$(function() {

    // Define the important CSS classes in one place.
    var SITEMAP_COLLAPSE_CONTROL_CLASS = "sitemap-collapse-control";
    
    // Global flag for disabling sitemap actions during updates.
    var sitemap_enabled = true;
    
    var sitemap = $("ul#sitemap");
    
    // Collapse the sitemap.
    $("li li", sitemap).addClass("closed");
    
    // Add the sitemap collapse control divs.
    $("li li:has(li)", sitemap).append($("<div/>").addClass(SITEMAP_COLLAPSE_CONTROL_CLASS));
    
    // Make the sitemap collapse controls clickable.
    $("div." + SITEMAP_COLLAPSE_CONTROL_CLASS, sitemap).click(function() {
        $(this).parent("li").toggleClass("closed");
    });

    // Make the sitemap controls clickable.
    $("button", sitemap).click(function() {
        // Prevent simultanious page moves.
        if (!sitemap_enabled) {
            return;
        }
        var button = $(this);
        var li = button.parents("li").slice(0, 1);
        var form = button.parents("form").slice(0, 1);
        var action = button.attr("value");
        if (action == "move-up") {
            var other_li = li.prev();
        } else if (action == "move-down") {
            var other_li = li.next();
        }
        // Check that there is something to exchange with.
        if (other_li.length > 0) {
            var data = form.serializeArray();
            data.push({
                name: "action",
                value: action
            });
            // Disable the sitemap.
            sitemap_enabled = false;
            // Trigger an AJAX call when the list item has faded out.
            li.fadeOut(function() {
                $.ajax({
                    url: form.attr("action"),
                    type: form.attr("method"),
                    data: data,
                    error: function() {
                        sitemap.remove();
                        $("div#sitemap-module").append($("<p/>").append("The sitemap service is currently unavailable."));
                    },
                    success: function(data) {
                        // Adnimate the page move.
                        if (action == "move-up") {
                            other_li.before(li);
                        } else if (action == "move-down") {
                            other_li.after(li);
                        }
                        li.fadeIn();
                        // Re-enable the sitemap.
                        sitemap_enabled = true
                    },
                    cache: false
                });
            });
        }
        return false;
    });

});

