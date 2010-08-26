from django.conf import settings
from django.core import serializers
from django.db.models import signals
from django.db.models.base import ModelBase
from django.template.loader import render_to_string

def default_repository_path(object):
    return "/%s/%s/%s" % (
        object._meta.app_label,
        object._meta.object_name,
        object.pk)

def default_repository_commit_message(object, created):
    return "Object %s (from '%s.%s') saved by django-vcexport." % (
        object.pk, object._meta.app_label, object._meta.object_name)

_utility = None
def get_utility():
    global _utility
    if _utility is not None:
        return _utility

    if not hasattr(settings, 'VCEXPORT_BACKEND'):
        backend = 'svn'
    else:
        backend = settings.VCEXPORT_BACKEND

    # defer imports so we don't end up with ImportErrors about pysvn 
    # or mercurial ii a user doesn't have them installed and isn't
    # trying to use a backend that needs them
    if backend == 'svn':
        from sven.backend import SvnAccess
        _utility = SvnAccess
        return SvnAccess
    if backend == 'hg':
        from sven.hg import HgAccess
        _utility = HgAccess
        return HgAccess
    if backend == 'bzr':
        from sven.bzr import BzrAccess
        _utility = BzrAccess
        return BzrAccess

class Exporter(object):

    repository_template = None

    def repository_path(self):
        return None
        
    def repository_commit_message(self, created):
        return None

    def repository_commit_user(self, created):
        return None

    def export_to_repository(self, 
                             created=False,
                             message=None):

        if message is None:
            message = self.repository_commit_message(created)

        repository_path = self.repository_path()

        repository_template = self.repository_template

        return export_to_repository(self.object,
                                    created, 
                                    message,
                                    repository_path,
                                    self.repository_template)

    def __init__(self, context):
        self.object = context

def export_to_repository(object,
                         created=False,
                         message=None,
                         repository_path=None,
                         repository_template=None):

    if message is None:
        message = default_repository_commit_message(object, created)

    if repository_path is None:
        repository_path = default_repository_path(object)

    context = {
        'object': object,
        'created': created,
        }
    if repository_template is not None:
        document = render_to_string(
            repository_template,
            context)
    else:
        document = serializers.get_serializer("xml")().serialize(
            object.__class__.objects.filter(pk=object.pk),
            indent=2)

    checkout_dir = settings.VCEXPORT_CHECKOUT_DIR

    backend_factory = get_utility()

    svn = backend_factory(checkout_dir)
    return svn.write(repository_path, document, msg=message)

def post_save_exporter(sender, instance, created, **kwargs):
    exporter = _registry.get(sender) or Exporter

    exportable = exporter(instance)
    exportable.export_to_repository(created=created)

_registry = {}
def register(cls, exporter=None):
    if exporter is not None:
        _registry[cls] = exporter
    
    signals.post_save.connect(post_save_exporter, sender=cls)
