/*
    Dynamic content for the CMS dashboard.
*/


$(function() {

    // Global flag for disabling sitemap actions during updates.
    var sitemap_enabled = true;
    
    var sitemap = $("ul#sitemap");
    
    // Collapse the sitemap.
    $("li li", sitemap).addClass("closed");
    
    // Make the sitemap collapse controls clickable.
    $("div.sitemap-collapse-control", sitemap).click(function() {
        $(this).parent("li").toggleClass("closed");
    });

    // Make the sitemap controls clickable.
    $("input[name=direction]", sitemap).click(function() {
        // Prevent simultanious page moves.
        if (!sitemap_enabled) {
            return;
        }
        var button = $(this);
        var li = button.parents("li").slice(0, 1);
        var form = button.parents("form").slice(0, 1);
        var direction = button.val();
        if (direction == "up") {
            var other_li = li.prev();
        } else if (direction == "down") {
            var other_li = li.next();
        }
        // Check that there is something to exchange with.
        if (other_li.length > 0) {
            var data = form.serializeArray();
            data.push({
                name: "direction",
                value: direction
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
                        // Animate the page move.
                        if (direction == "up") {
                            other_li.before(li);
                        } else if (direction == "down") {
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

