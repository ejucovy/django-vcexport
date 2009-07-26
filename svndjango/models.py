from django.db.models.fields import TextField
class SubversionedTextField(TextField):
    pass

class SubversionedMixin(object):
    def save(self, *args, **kw):
        from django.conf import settings
        svn_checkout_dir = settings.SVNDJANGO_CHECKOUT_DIR
        svn_repo_location = None #sven bug - this is unused

        if getattr(settings, 'SVNDJANGO_SILENT_FAILURES', None) is True:
            try:
                save_to_svn(self,
                            default_name_mapper, default_serializer,
                            svn_checkout_dir, svn_repo_location)
            except:
                pass
        else:
            save_to_svn(self,
                        default_name_mapper, default_serializer,
                        svn_checkout_dir, svn_repo_location)
            

from django.db import models
class SubversionedModel(models.Model, SubversionedMixin):
    def save(self, *args, **kw):
        models.Model.save(self, *args, **kw)
        SubversionedMixin.save(self, *args, **kw)


class SVNDoc(object):
    def save(self, *args, **kw):
        versioned_fields = (i.name for i in self._meta.fields
                            if isinstance(i, SubversionedTextField))
        from django.conf import settings
        svn_checkout_dir = settings.SVNDJANGO_CHECKOUT_DIR
        svn_repo_location = None #sven bug - this is unused
        
        for field in versioned_fields:
            if getattr(settings, 'SVNDJANGO_SILENT_FAILURES', None) is True:
                try:
                    save_to_svn(self,
                                attribute_name_mapper(field),
                                attribute_serializer(field),
                                svn_checkout_dir, svn_repo_location)
                except:
                    pass
            else:
                save_to_svn(self,
                            attribute_name_mapper(field),
                            attribute_serializer(field),
                            svn_checkout_dir, svn_repo_location)

def save_to_svn(obj,
                name_mapper, serializer,
                svn_checkout_dir, svn_repo_location,
                user=None, mimetype=None):
    uri = path_to_obj_relative_to_svn_site_root = name_mapper(obj)

    document = serializer(obj, mimetype)

    from sven.backend import SvnAccess

    svn = SvnAccess(svn_repo_location, svn_checkout_dir)

    svn.write(uri, document)
    
def default_name_mapper(obj):    
    return '/'.join((obj.__class__.__module__.replace('.', '/'),
                     obj.__class__.__name__,
                     unicode(obj.pk)))

class attribute_name_mapper(object):
    def __init__(self, attr):
        self.attr = attr

    def __call__(self, obj):
        return '/'.join((default_name_mapper(obj),
                         self.attr))

def default_serializer(obj, mimetype=None):
    mimetype = 'application/json'

    from django.core import serializers
    return serializers.serialize('json', [obj])

class attribute_serializer(object):
    def __init__(self, attr):
        self.attr = attr

    def __call__(self, obj, mimetype=None):
        return getattr(obj, self.attr)

