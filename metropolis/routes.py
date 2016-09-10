"""A collection of all the routes."""

from pyramid.response import Response


def test(request):
    """Test handler."""
    return Response('helloj world!')
