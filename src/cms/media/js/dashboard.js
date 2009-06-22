/*
    Dynamic content for the CMS dashboard.
*/


$(function() {
    
    // Collapse the sitemap.
    $("ul#sitemap li li").addClass("closed");
    
    // Add the sitemap collapse control divs.
    $("ul#sitemap li li:has(li)").append('<div class="sitemap-collapse-control"/>');
    
    // Make the sitemap collapse controls clickable.
    $("div.sitemap-collapse-control").click(function() {
        $(this).parent("li").toggleClass("closed");
    });
    
});

