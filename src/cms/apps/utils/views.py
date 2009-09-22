"""Some utility views."""


from django.shortcuts import render_to_response


def link_dialogue(request):
    """Renders the insert link dialogue for the rich text editor."""
    context = {}
    