/*
    TinyMCE external link list.
*/


var tinyMCELinkList = new Array(
    {% for title, permalink in links %}
        ["{{title|escapejs}}", "{{permalink|escapejs}}"]{% if not forloop.last %},{% endif %}
    {% endfor %}
);