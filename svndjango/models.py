from django.conf import settings
from django.db.models import signals
from django.db.models.base import ModelBase
from django.template.loader import render_to_string

class VersionedMixin(object):
    repository_template = 'vcsexport/default.xml'

    def repository_path(self):
        return "/%s/%s/%s" % (
            self._meta.app_label,
            self._meta.object_name,
            self.pk)
        
    def repository_commit_message(self, request, created):
        return "Object %s (from '%s.%s') saved by django-vcsexport." % (
            self.pk, self._meta.app_label, self._meta.object_name)

    def repository_commit_user(self, request, created):
        return None

    def export_to_repository(self, request=None, created=False):
        context = {
            'object': self,
            'created': created,
            }
        
        document = render_to_string(
            self.repository_template,
            context)

        path = self.repository_path()

        commit_message = self.repository_commit_message(
            request, created)
        user = self.repository_commit_user(
            request, created)

        checkout_dir = settings.VCSEXPORT_CHECKOUT_DIR

        svn = SvnAccess(checkout_dir)
        return svn.write(path, document, msg=commit_message, user=user)

def export_to_repository(sender, instance, created, **kwargs):
    instance.export_to_repository(created=created)

if getattr(settings, 'VCSEXPORT_AUTO_SAVE', True):
    signals.post_save.connect(export_to_repository, sender=VersionedMixin)

