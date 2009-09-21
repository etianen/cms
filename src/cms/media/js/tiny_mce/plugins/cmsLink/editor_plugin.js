/**
 * Custom hyperlink generation plugin.
 * 
 * Developed exclusively for the Etianen.com Content Management System. 
 */

(function() {

    tinymce.PluginManager.requireLangPack("cmsLink");
    
    tinymce.create("tinymce.plugins.CMSLinkPlugin", {
        
        /*
         * Initializes the plugin.
         */
        init: function(ed, url) {
    
            // Register commands
            ed.addCommand("cmsLink", function() {
                var se = ed.selection;
    
                // No selection and not in link
                if (se.isCollapsed() && !ed.dom.getParent(se.getNode(), "A"))
                    return;
    
                ed.windowManager.open({
                    file: url + "/dialog.html",
                    width: 480,
                    height: 400,
                    inline: 1
                }, {
                    plugin_url: url
                });
            });
    
            // Register buttons
            ed.addButton("link", {
                title: "cmsLink.desc",
                cmd: "cmsLink"
            });
    
            ed.addShortcut("ctrl+k", "cmsLink.desc", "cmsLink");
    
            ed.onNodeChange.add(function(ed, cm, n, co) {
                cm.setDisabled("cmsLink", co && n.nodeName != "A");
                cm.setActive("cmsLink", n.nodeName == "A" && !n.name);
            });
        },

        /*
         * Not used.
         */
        createControl: function(n, cm) {
            return null;
        },

        /*
         * Returns information about this plugin.
         */
        getInfo: function() {
            return {
                longname: "Etianen.com CMS Link Plugin",
                author: "David Hall",
                authorurl: "http://www.etianen.com/",
                infourl: "http://www.etianen.com/",
                version: "1.0"
            };
        }
    });

    // Register plugin
    tinymce.PluginManager.add("cmsLink", tinymce.plugins.CMSLinkPlugin);
    
})();

