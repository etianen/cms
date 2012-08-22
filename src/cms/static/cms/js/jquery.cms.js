/*
    Scripting for the CMS admin.
*/


(function($) {
    
    /**
     * The main cms plugin. Use by passing in the name of the required method.
     */
    var cms = $.fn.cms = function(method) {
        if (cms[method]) {
            return cms[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else {
            $.error("Method " +  method + " does not exist on jQuery.cms");
        }
    }
    
    // Namespace for static cms plugins.
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
     * Activates a rich text area.
     */
    cms.htmlWidget = function(config) {
        // Configure the plugin.
        var settings = $.extend({
            mode: "exact",
            setup: function(editor) {
                editor.onPostProcess.add(function(editor, o) {
                    o.content = o.content.replace(/&nbsp;/g, " ").replace(/ +/g, " ");
                });
            }
        }, cms.htmlWidget.extensions, config)
        // Run the plugin.
        return this.each(function() {
            var container = $(this);
            var state = container.data("cms.htmlWidget");
            if (!state) {
            	state = {};
            	container.data("cms.htmlWidget", state);
            }
            if (!state.initialized) {
            	if (container.not(".inline-group .empty-form textarea").length) {
            		tinyMCE.init($.extend({
                        elements: container.attr("id"),
                    }, settings));
                	state.initialized = true;
            	} else {
            		// Set up deferred initialization.
            		if (!state.initializedDeferred) {
                		setTimeout(function() {
                			var parentContainer = container.parents(".inline-group");
                    		parentContainer.find(".add-row a").click(function() {
                    			parentContainer.find("textarea").cms("htmlWidget", config);
                    		});
                		});
                		state.initializedDeferred = true;
            		}
            	}
            }
        });
    }
    
    // Extensions for the html widget.
    cms.htmlWidget.extensions = {};
    
}(django.jQuery));