/*
    A list of TinyMCE images.
*/


{% load pages %}


var tinyMCEImageList = new Array(
    {% for image in images %}
        ["{{image.title|escapejs}}", "{{image|permalink|escapejs}}"]{% if not forloop.last %},{% endif %}
    {% endfor %}
);

