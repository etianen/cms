/*
    Scripting for the CMS admin.
*/


(function($) {
    
    // Namespace for cms plugins.
    var cms = {};
    
    /**
     * The main cms plugin. Use by passing in the name of the required method.
     */
    $.fn.cms = function(method) {
        if (cms[method]) {
            return cms[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else {
            $.error("Method " +  method + " does not exist on jQuery.cms");
        }
    }
    
    // Namespace for cms static plugins.
    $.cms = {};
    
    /**
     * Gets the value of a named cookie.
     */
    $.cms.cookie = function(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != "") {
            var cookies = document.cookie.split(";");
            for (var i = 0; i < cookies.length; i++) {
                var cookie = $.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    /**
     * Disables text selection on the given element.
     */
    cms.disableTextSelect = function() {
        return this.each(function() {
        	if ($.browser.mozilla) {
        		$(this).css('MozUserSelect', 'none');
        	 } else if ($.browser.msie) {
        		$(this).bind('selectstart', function () {
        		    return false;
        		});
        	} else {
        		$(this).mousedown(function() {
        		    return false;
        		});
        	}
        });
    }
    
    /**
     * Activates the main CMS dashboard sitemap.
     */
    cms.sitemap = function() {
        return this.each(function() {
            // Global flag for disabling sitemap actions during updates.
            var sitemap_enabled = true;
            // Get some containers.
            var sitemap = $(this);
            var container = $('<div/>')
            sitemap.append(container)
            var loader = $('<p class="loading">Loading sitemap...</p>');
            container.append(loader);
            container.height(container.height());
            loader.hide().fadeIn(function() {
                $.getJSON("/admin/sitemap.json", function(data) {
                    loader.fadeOut(function() {
                        var dataContainer = $("<div>").css("opacity", 0);
                        // Process data.
                        if (data.entries.length > 0) {
                            var homepageList = $('<ul/>');
                            function addEntry(depth, list, index, page, siblings) {
                                var li = $('<li/>');
                                // Add the collapse control.
                                if (depth > 0 && page.children.length > 0) {
                                    var collapseControl = $('<div class="sitemap-collapse-control"></div>');
                                    li.append(collapseControl);
                                    collapseControl.click(function() {
                                        li.toggleClass("closed");
                                    });
                                    li.addClass("closed");
                                }
                                // Generate the URLs.
                                function createPageUrl(url) {
                                    return url.replace("__id__", page.id);
                                }
                                var addUrl = createPageUrl(data.addUrl);
                                var changeUrl = createPageUrl(data.changeUrl);
                                var deleteUrl = createPageUrl(data.deleteUrl);
                                // Add the detail container.
                                var pageContainer = $('<div class="sitemap-entry"/>');
                                if (page.isOffline) {
                                    pageContainer.addClass("offline");
                                }
                                if (page.canChange) {
                                    pageContainer.addClass("can-change");
                                    pageContainer.append('<a href="' + changeUrl + '" class="title" title="Edit this page">' + page.title + '</a>');
                                } else {
                                    pageContainer.append('<span class="title">' + page.title + '</span>');
                                }
                                if (data.canAdd) {
                                    pageContainer.append('<a href="' + addUrl + '" class="addlink" title="Add a new page underneath this page">Add</a>');
                                }
                                if (page.canChange) {
                                    pageContainer.append('<a href="' + changeUrl + '" class="changelink" title="Edit this page">Change</a>');
                                }
                                if (page.canDelete) {
                                    pageContainer.append('<a href="' + deleteUrl + '" class="deletelink" title="Delete this page">Delete</a>');
                                }
                                // Add the move functionality.
                                if (page.canChange && data.moveUrl) {
                                    function makeMoveHandler(direction) {
                                        return function() {
                                            // Prevent simultanious page moves.
                                            if (!sitemap_enabled) {
                                                return;
                                            }
                                            if (direction == "up") {
                                                var other_li = li.prev();
                                            } else if (direction == "down") {
                                                var other_li = li.next();
                                            }
                                            // Disable the sitemap.
                                            sitemap_enabled = false;
                                            // Trigger an AJAX call when the list item has faded out.
                                            li.fadeOut(function() {
                                                $.ajax({
                                                    url: data.moveUrl,
                                                    type: "POST",
                                                    data: {
                                                        page: page.id,
                                                        direction: direction
                                                    },
                                                    beforeSend: function(xhr, settings) {
                                                        xhr.setRequestHeader("X-CSRFToken", $.cms.cookie("csrftoken"));
                                                    },
                                                    error: function() {
                                                        dataContainer.fadeOut(function() {
                                                            container.append('<p>The sitemap service is currently unavailable.</p>');
                                                        });
                                                    },
                                                    success: function(data) {
                                                        // Animate the page move.
                                                        if (direction == "up") {
                                                            other_li.before(li);
                                                        } else if (direction == "down") {
                                                            other_li.after(li);
                                                        }                                                        
                                                        li.fadeIn();
                                                        // Re-render the list items.
                                                        li.trigger("render.cms");
                                                        other_li.trigger("render.cms");
                                                        // Re-enable the sitemap.
                                                        sitemap_enabled = true
                                                    },
                                                    cache: false
                                                });
                                            });
                                        }
                                    }
                                    // Add the move controls.
                                    var moveUp = $('<span class="move-up" title="Move this page up"/>')
                                    pageContainer.append(moveUp);
                                    moveUp.click(makeMoveHandler("up"));
                                    var moveDown = $('<span class="move-down" title="Move this page down"/>');
                                    pageContainer.append(moveDown);
                                    moveDown.click(makeMoveHandler("down"));
                                    // Add in the render event.
                                    li.bind("render.cms", function() {
                                        // Show / hide the move controls.
                                        if (li.prev().length > 0) {
                                            moveUp.show();
                                        } else {
                                            moveUp.hide();
                                        }
                                        if (li.next().length > 0) {
                                            moveDown.show();
                                        } else {
                                            moveDown.hide();
                                        }
                                    });
                                }
                                li.append(pageContainer);
                                // Add in the children.
                                if (page.children.length > 0) {
                                    var childList = $('<ul/>');
                                    $.each(page.children, function(index, child) {
                                        addEntry(depth + 1, childList, index, child, page.children);
                                    });
                                    li.append(childList);
                                }
                                // Add in the list.
                                list.append(li);
                            }
                            addEntry(0, homepageList, 0, data.entries[0], data.entries);
                            homepageList.find("li").trigger("render.cms");
                            dataContainer.append(homepageList);
                        } else {
                            dataContainer.append("<p>This site doesn't have a homepage.</p>");
                            if (data.canAdd) {
                                dataContainer.append('<p>It\'s time to go ahead and <a href="' + data.createHomepageUrl + '">create one</a>!</p>');
                            }
                        }
                        // Disable text selection.
                        dataContainer.cms("disableTextSelect");
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
    }
    
}(django.jQuery));