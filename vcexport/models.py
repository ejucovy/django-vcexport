from django.conf import settings
from django.core import serializers
from django.db.models import signals
from django.db.models.base import ModelBase
from django.template.loader import render_to_string

from sven.backend import SvnAccess

class VersionedMixin(object):
    repository_template = None

    def repository_path(self):
        return "/%s/%s/%s" % (
            self._meta.app_label,
            self._meta.object_name,
            self.pk)
        
    def repository_commit_message(self, request, created):
        return "Object %s (from '%s.%s') saved by django-vcexport." % (
            self.pk, self._meta.app_label, self._meta.object_name)

    def repository_commit_user(self, request, created):
        return None

    def export_to_repository(self, request=None, created=False,
                             message=None, username=None):
        context = {
            'object': self,
            'created': created,
            }
        
        if self.repository_template is not None:
            document = render_to_string(
                self.repository_template,
                context)
        else:
            document = serializers.get_serializer("xml")().serialize(
                self.__class__.objects.filter(pk=self.pk),
                indent=2)

        path = self.repository_path()

        if message is None:
            message = self.repository_commit_message(
                request, created)

        #if username is None:
        #    username = self.repository_commit_user(request, created)

        checkout_dir = settings.VCEXPORT_CHECKOUT_DIR

        svn = SvnAccess(checkout_dir)
        return svn.write(path, document, msg=message) #, user=username)

def export_to_repository(sender, instance, created, **kwargs):
    instance.export_to_repository(created=created)

def register(cls):
    signals.post_save.connect(export_to_repository, sender=cls)
