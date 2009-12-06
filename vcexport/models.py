from django.conf import settings
from django.core import serializers
from django.db.models import signals
from django.db.models.base import ModelBase
from django.template.loader import render_to_string

from sven.backend import SvnAccess

class Exporter(object):
    repository_template = None

    def repository_path(self):
        return "/%s/%s/%s" % (
            self.object._meta.app_label,
            self.object._meta.object_name,
            self.object.pk)
        
    def repository_commit_message(self, created):
        return "Object %s (from '%s.%s') saved by django-vcexport." % (
            self.object.pk, self.object._meta.app_label, self.object._meta.object_name)

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
                self.object.__class__.objects.filter(pk=self.pk),
                indent=2)

        path = self.repository_path()

        if message is None:
            message = self.repository_commit_message(created)

        #if username is None:
        #    username = self.repository_commit_user(created)

        checkout_dir = settings.VCEXPORT_CHECKOUT_DIR

        svn = SvnAccess(checkout_dir)
        return svn.write(path, document, msg=message) #, user=username)

    def __init__(self, context):
        self.object = context


def export_to_repository(sender, instance, created, **kwargs):
    exporter = _registry.get(sender) or Exporter

    exportable = exporter(instance)
    exportable.export_to_repository(created=created)

_registry = {}
def register(cls, exporter=None):
    if exporter is not None:
        _registry[cls] = exporter
    
    signals.post_save.connect(export_to_repository, sender=cls)
