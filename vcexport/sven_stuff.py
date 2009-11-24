"""
Some optional stuff for/about sven. Experimental.

You can (potentially) use DjangoAutoupdatingSvnAccess as a Sven backend
which will update your django database when repository content changes.
"""

def deserialize(uri, contents, msg, kind, revs):
    from django.core import serializers

    object = serializers.deserialize('json', contents)

    for obj in object:
        obj.save()

from sven.backend import SvnAccessEventEmitter as SvnAccess
class DjangoAutoupdatingSvnAccess(SvnAccess):
    def __init__(self, *args, **kw):
        SvnAccess.__init__(self, *args, **kw)
        self.listeners = [deserialize]

