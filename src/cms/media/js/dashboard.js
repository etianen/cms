/*
    Dynamic content for the CMS dashboard.
*/


(function($) {
    $(function() {
    
        // Global flag for disabling sitemap actions during updates.
        var sitemap_enabled = true;
        
        $("#sitemap-module").each(function() {
            var sitemap = $(this);
            var container = $('<div/>').css("padding-bottom", "1px");
            sitemap.append(container)
            var loader = $('<p class="loading">Loading sitemap...</p>');
            container.append(loader);
            container.height(container.height());
            loader.hide().fadeIn(function() {
                $.getJSON("/admin/pages/page/sitemap.json", function(data) {
                    loader.fadeOut(function() {
                        var dataContainer = $("<div>").css("opacity", 0).css("padding-bottom", "1px");
                        // Process data.
                        if (data.canChange) {
                            if (data.entries.length > 0) {
                                var homepageList = $('<ul/>');
                                function addEntry(list, page) {
                                    var li = $('<li/>');
                                    // Add the collapse control.
                                    if (page.hasParent && page.children.length > 0) {
                                        var collapseControl = $('<div class="sitemap-collapse-control"></div>');
                                        li.append(collapseControl);
                                        collapseControl.click(function() {
                                            li.toggleClass("closed");
                                        });
                                        li.addClass("closed");
                                    }
                                    // Add the detail container.
                                    var pageContainer = $('<div class="sitemap-entry"/>');
                                    if (page.isOffline) {
                                        pageContainer.addClass("offline");
                                    }
                                    if (page.canChange) {
                                        pageContainer.addClass("can-change");
                                        pageContainer.append('<a href="' + page.changeUrl + '" class="title" title="Edit this page">' + page.title + '</a>');
                                    } else {
                                        pageContainer.append('<span class="title">' + page.title + '</span>');
                                    }
                                    if (data.canAdd) {
                                        pageContainer.append('<a href="' + page.addUrl + '" class="addlink" title="Add a new page underneath this page">Add</a>');
                                    }
                                    if (page.canChange) {
                                        pageContainer.append('<a href="' + page.changeUrl + '" class="changelink" title="Edit this page">Change</a>');
                                    }
                                    if (page.canDelete) {
                                        pageContainer.append('<a href="' + page.deleteUrl + '" class="deletelink" title="Delete this page">Delete</a>');
                                    }
                                    li.append(pageContainer);
                                    // Add in the children.
                                    if (page.children.length > 0) {
                                        var childList = $('<ul/>');
                                        $.each(page.children, function(_, child) {
                                            addEntry(childList, child);
                                        });
                                        li.append(childList);
                                    }
                                    // Add in the list.
                                    list.append(li);
                                }
                                addEntry(homepageList, data.entries[0]);
                                dataContainer.append(homepageList);
                            } else {
                                dataContainer.append("<p>This site doesn't have a homepage.</p>");
                                if (data.canAdd) {
                                    dataContainer.append('<p>It\'s time to go ahead and <a href="' + data.createHomepageUrl + '">create one</a>!</p>');
                                }
                            }
                        } else {
                            dataContainer.append("<p>You do not have permission to view this site's pages.</p>");
                        }
                        // Fade in data.
                        container.append(dataContainer);
                        container.animate({
                            height: dataContainer.height()
                        }, {
                            complete: function() {
                                container.css("height", "auto");
                                dataContainer.animate({
                                    opacity: 1
                                });
                            }
                        });
                    });
                });
            });
        });
        
        
        
        
        
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
}(django.jQuery));