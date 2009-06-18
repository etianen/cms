/*
    A list of TinyMCE links.
*/


{% load pages %}


var tinyMCELinkList = new Array(
    {% for file in files %}
        ["{{file.title|escapejs}}", "{{file|permalink|escapejs}}"]{% if not forloop.last %},{% endif %}
    {% endfor %}
);

