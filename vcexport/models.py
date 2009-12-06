from django.conf import settings
from django.core import serializers
from django.db.models import signals
from django.db.models.base import ModelBase
from django.template.loader import render_to_string

from sven.backend import SvnAccess

def default_repository_path(object):
    return "/%s/%s/%s" % (
        object._meta.app_label,
        object._meta.object_name,
        object.pk)

def default_repository_commit_message(object, created):
    return "Object %s (from '%s.%s') saved by django-vcexport." % (
        object.pk, object._meta.app_label, object._meta.object_name)


class Exporter(object):
    repository_template = None

    def repository_path(self):
        return default_repository_path(self.object)
        
    def repository_commit_message(self, created):
        return default_repository_commit_message(self.object, created)

    def repository_commit_user(self, created):
        return None

    def export_to_repository(self, 
                             created=False,
                             message=None, username=None):
        context = {
            'object': self.object,
            'created': created,
            }
        
        if self.repository_template is not None:
            document = render_to_string(
                self.repository_template,
                context)
        else:
            document = serializers.get_serializer("xml")().serialize(
                self.object.__class__.objects.filter(pk=self.object.pk),
                indent=2)

        path = self.repository_path()

        if message is None:
            message = self.repository_commit_message(created)

        #if username is None:
        #    username = self.repository_commit_user(created)

        return export_to_repository(self.object,
                                    created, message, username,
                                    repository_template)

    def __init__(self, context):
        self.object = context

def export_to_repository(object,
                         created=False,
                         message=None,
                         repository_path=None,
                         repository_template=None):
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

    path = repository_path or default_repository_path(object)

    if message is None:
        message = default_repository_commit_message(object, created)

    #if username is None:
    #    username = default_repository_commit_user(object, created)

    checkout_dir = settings.VCEXPORT_CHECKOUT_DIR

    svn = SvnAccess(checkout_dir)
    return svn.write(path, document, msg=message) #, user=username)

def post_save_exporter(sender, instance, created, **kwargs):
    exporter = _registry.get(sender) or Exporter

    exportable = exporter(instance)
    exportable.export_to_repository(created=created)

_registry = {}
def register(cls, exporter=None):
    if exporter is not None:
        _registry[cls] = exporter
    
    signals.post_save.connect(post_save_exporter, sender=cls)
