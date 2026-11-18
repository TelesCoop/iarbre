"""Business logic used by the API views.

Services take and return plain Python objects (geometries, querysets, dicts,
bytes). They know nothing about ``request`` or ``Response``: parsing input,
choosing serializers and HTTP status codes stay in ``api.views``.
"""
