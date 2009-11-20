This package provides some basic utilities for backing up django model
instances to a version-controlled repository. It is very experimental
at this point and hasn't been tested in any meaningful environment.

It does not provide any utilities for restoring live data from backups.

How it works
============

1. It defines a post_save signal listener which serializes to a text
   format and saves to the repository. You can disable the signal
   in settings.py (see below)

2. Each model that you wish to version should subclass its VersionedMixin
   model.

3. By default, models are serialized to django's XML format, because it
   works well with `diff` and is generic.

4. You can customize the serialization per model by passing a custom
   template path as a class attribute:
    
     class MyModel(models.Model, VersionedMixin):
         repository_template = 'fleem/document_format.txt'

   The template will be rendered with two context variables; ``object``
   which is the model instance that was saved, and a boolean ``created``

     {% if created %}New object!{% endif %}
     {{object.title}}
     {{object.related_field.pk}}
       ****
     Color: {{object.color}}
     {{object.description}}

This allows alternate use cases to be supported:

* You want to version a model wholesale
* You have a model which has one or two document-like text fields, and you
  want to version those fields only

To be honest, versioning a model wholesale seems like a pretty bad idea to
me, unless you're very careful about versioning every related model, and
unless you're versioning the model schemas side-by-side with the content.
But it's fun to experiment with at least.

*** NOT YET IMPLEMENTED ******
* You can also customize the *
* default serialization      *
* globally by overriding     *
* the template               *
* ``vcsexport/default.xml``  *
* with your own.             *
******************************

By default your model instances will be serialized to JSON and saved in
repository paths that look like `/app_name/ModelClassName/instance_pk`.

You can customize the path:

  class MyModel(models.Model, VersionedMixin):
      def repository_path(self):
          return '/my_custom/path_for/this_model/' + self.color

Note that if you do this, you may end up with multiple model instances
that save to the same file path in the repository. This is a feature.

The default commit message is uninteresting: "Object {{instance.pk}}
(from '{{app_name}}.{{model_name}}') saved by django-vcsexport."

The default committing user is undefined.

You can customize both, with model methods that take a request object
and a boolean ``created``, and return strings:

  class MyModel(models.Model, VersionedMixin):
      def repository_commit_message(self, request, created):
          if created:
              return "User %s committed a new %s" % (request.user.username, self.color)
          return "User %s committed %s" % (request.user.username, self.color)

      def repository_commit_user(self, request, created):
          return request.user.username

******** NOT YET IMPLEMENTED: username ***********

Unfortunately, `request` will be None if you use the automatic post_save
signal. If you want to use data from the request, you should disable the
signal (see below) and explicitly export the content after a save:

  def my_view(request):
      ...
      versioned_object, created = MyModel.objects.get_or_create(...)
      versioned_object.save()
      versioned_object.export_to_repository(request, created)

Both ``request`` and ``created`` are optional and default to None and
False respectively. You can also pass a commit message and/or username
to `export_to_repository` directly:

  versioned_object.export_to_repository(message="Foo", 
                                        username=request.user.username)

The method will return the Revision of the commit, or None if there
were no changes to apply.

You must provide one piece of configuration in your settings.py file:

* VCSEXPORT_CHECKOUT_DIR: the absolute path to a local checkout of the
  repository that you want to store your data in

You can optionally provide a configuration setting to disable automatic
saves with the post_save signal:

  VCSEXPORT_AUTO_SAVE = False

You will have to initialize your repository and checkout on your own.

You must have pysvn installed.

Originally developed at Columbia University's Center for New Media
Teaching & Learning <http://ccnmtl.columbia.edu>
