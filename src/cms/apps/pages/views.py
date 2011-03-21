"""Base views used by page models."""


from django.shortcuts import render


def index(request):
    """Renders the default index page for page content."""
    return render(request, "base.html", {})