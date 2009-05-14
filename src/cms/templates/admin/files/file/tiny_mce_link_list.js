/*
    Renders the TinyMCE link list.
*/
{% load permalinks %}


var tinyMCELinkList = new Array(
    {% for file in files %}
        ["{{file.title|escapejs}}", "{{file|permalink|escapejs}}"]{% if not forloop.last %},{% endif %}
    {% endfor %}
);

