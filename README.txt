This package provides some basic utilities for backing up django model
instances to a version-controlled repository. It is very experimental
at this point and hasn't been tested in any meaningful environment.

It does not provide any utilities for restoring live data from backups.

How it works
============

1. It defines a post_save signal listener which serializes to a text
   format and saves to the repository.

2. Each model that you wish to version should subclass its VersionedMixin
   model.

3. By default, models are serialized to django's XML format, because it
   works well with `diff` and is generic.

4. You can customize the serialization per model by passing a custom
   template path in its metaclass:
    
     class MyModel(models.Model, VersionedMixin):
         class Meta:
             repository_template = 'fleem/document_format.txt'

   The template will be rendered with a single context variable ``object``
   which is the model instance that was saved:

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

By default your model instances will be serialized to JSON and saved in
repository paths that look like `/app_name/model_class_name/instance_pk`.

You can customize the path:

  class MyModel(models.Model, VersionedMixin):
      class Meta:
          repository_path_prefix = '/my_custom/path_for/this_model/'
	  repository_path_instance_attribute = 'color'

Or if you want complete control:

  class MyModel(models.Model, VersionedMixin):
      def repository_path(self):
          return '/my_custom/path_for/this_model/' + self.color

Note that if you do this, you may end up with multiple model instances
that save to the same file path in the repository. This is a feature.

The default commit message is uninteresting: "Object {{instance.pk}}
(from '{{app_name}}.{{model_name}}') saved by django-vcsexport."

The default committing user is undefined.

You can customize both, with model methods that take a request object
and return strings:

  class MyModel(models.Model, VersionedMixin):
      def repository_path(self):
          return '/my_custom/path_for/this_model/' + self.color

      def repository_commit_message(self, request):
          return "User %s committed %s" % (request.user.username, self.color)

      def repository_commit_user(self, request):
          return request.user.username

You must provide one piece of configuration in your settings.py file:

* VCSEXPORT_CHECKOUT_DIR: the absolute path to a local checkout of the
  repository that you want to store your data in

You will have to initialize your repository and checkout on your own.

You must have pysvn installed.

Originally developed at Columbia University's Center for New Media
Teaching & Learning <http://ccnmtl.columbia.edu>
