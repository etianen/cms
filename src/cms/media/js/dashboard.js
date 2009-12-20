/*
    Dynamic content for the CMS dashboard.
*/


$(function() {

    var SITEMAP_COLLAPSE_CONTROL_CLASS = "sitemap-collapse-control";
    var SITEMAP_ENTRY_CLASS = "sitemap-entry";
    var SITEMAP_MOVE_UP_CLASS = "move-up";
    var SITEMAP_MOVE_DOWN_CLASS = "move-down";
    
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
    
    // Add the move controls.
    var moveUpControl = $("<div/>").attr("title", "Move this page up").addClass(SITEMAP_MOVE_UP_CLASS);
    var moveDownControl = $("<div/>").attr("title", "Move this page down").addClass(SITEMAP_MOVE_DOWN_CLASS);
    $("li li div.can-change." + SITEMAP_ENTRY_CLASS, sitemap).append(moveUpControl).append(moveDownControl);
    
    // Generates the page ID from the given list item.
    function getPageID(li) {
        var entry = $("div." + SITEMAP_ENTRY_CLASS, li);
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
                    error: function() {
                        sitemap.remove();
                        $("div#sitemap-module").append($("<p/>").append("The sitemap service is currently unavailable."));
                    },
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
    $("div." + SITEMAP_MOVE_UP_CLASS).click(function() {
        movePage(this, "up");
    });
    
    // Make the move down controls clickable.
    $("div." + SITEMAP_MOVE_DOWN_CLASS).click(function() {
        movePage(this, "down");
    });
    
});

