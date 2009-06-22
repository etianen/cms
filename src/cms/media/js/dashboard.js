/*
    Dynamic content for the CMS dashboard.
*/


$(function() {

    // Global flag for disabling sitemap actions during updates.
    var sitemap_enabled = true;
    
    // Collapse the sitemap.
    $("ul#sitemap li li").addClass("closed");
    
    // Add the sitemap collapse control divs.
    $("ul#sitemap li li:has(li)").append('<div class="sitemap-collapse-control"/>');
    
    // Make the sitemap collapse controls clickable.
    $("div.sitemap-collapse-control").click(function() {
        $(this).parent("li").toggleClass("closed");
    });
    
    // Add the move controls.
    $("ul#sitemap li li.can-change div.sitemap-entry").append('<div title="Move this page up" class="move-up"/><div title="Move this page down" class="move-down"/>');
    
    // Displays an error message in the sitemap.
    function displayError() {
        $("ul#sitemap").remove();
        $("div#sitemap-module").append("<p>The sitemap service is currently unavailable.</p>");
    }
    
    // Generates the page ID from the given list item.
    function getPageID(li) {
        var entry = $("div.sitemap-entry", li);
        return $(entry).attr("id").split("-")[2];
    }
    
    // Moves a page in the given direction.
    function movePage(control, direction) {
        if (!sitemap_enabled) {
            return;
        }
        var li = $($(control).parents("li").get(0));
        var page_id = getPageID(li);
        if (direction == "up") {
            var other_li = li.prev();
        } else if (direction == "down") {
            var other_li = li.next();
        }
        var other_id = getPageID(other_li);
        // Check that there is something to exchange with.
        if (other_li.length > 0) {
            // Disable the sitemap.
            sitemap_enabled = false;
            // Trigger an AJAX call when the list item has faded out.
            li.fadeOut(function() {
                $.ajax({
                    url: "/admin/reorder-pages/",
                    type: "POST",
                    data: {
                        pages: [page_id, other_id]
                    },
                    error: displayError,
                    success: function(data) {
                        // Adnimate the page move.
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
    }
    
    // Make the move up controls clickable.
    $("div.move-up").click(function() {
        movePage(this, "up");
    });
    
    // Make the move down controls clickable.
    $("div.move-down").click(function() {
        movePage(this, "down");
    });
    
});

