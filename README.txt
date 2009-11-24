This package provides some basic utilities for backing up django model
instances to a version-controlled repository. It is very experimental
at this point and hasn't been tested in any meaningful environment.

It does not provide any utilities for restoring live data from backups.

How it works
============

1. Each model that you wish to version should subclass vcexport's
   models.VersionedMixin class. It defines an `export_to_repository`
   method which serializes the instance to a text format and saves
   to the repository.

2. For automatic versioning of models, register them with vcexport::

     import vcexport
     vcexport.register(MyModel)

   This will connect a post_save signal.

3. By default, models are serialized to django's XML format, because it
   works well with `diff` and is generic.

4. You can customize the serialization per model by passing a custom
   template path as a class attribute::
    
     class MyModel(models.Model, VersionedMixin):
         repository_template = 'fleem/document_format.txt'

   The template will be rendered with two context variables; ``object``
   which is the model instance that was saved, and a boolean ``created``::

     {% if created %}New object!{% endif %}
     {{object.title}}
     {{object.related_field.pk}}
       ****
     Color: {{object.color}}
     {{object.description}}

   This allows alternate use cases to be supported:

    * You want to version a model wholesale
    * You have a model which has one or two document-like text fields, 
      and you want to version those fields only -- just don't write out
      any other fields in the serialization template.

5. By default the document dumps of your model instances will be saved in
   repository paths that look like `/app_name/ModelClassName/instance_pk`.

   You can customize the path::

     class MyModel(models.Model, VersionedMixin):
         def repository_path(self):
     	     return '/my_custom/path_for/this_model/' + self.color

   Note that if you do this, you may end up with multiple model instances
   that save to the same file path in the repository. This is a feature.

6. The default commit message is uninteresting: "Object {{instance.pk}}
   (from '{{app_name}}.{{model_name}}') saved by django-vcexport."

   The default committing user is undefined. At present you cannot
   customize this.

   You can customize the commit message with a model method that
   takes a request object and a boolean ``created``, and returns 
   a string::

     class MyModel(models.Model, VersionedMixin):
         def repository_commit_message(self, request, created):
             if created:
                 return "User %s committed a new %s" % (
 		   request.user.username, self.color)
             return "User %s committed %s" % (request.user.username, 
	     	    	     	       	      self.color)

7. You can also export the content explicitly, for example in your model's
   .save() method, in view code, etc. Use the ``export_to_repository``
   method, which, like ``repository_commit_message`` and ``repository_commit_user``,
   optionally takes a ``request`` argument. This allows you to encapsulate
   your logic for getting relevant data out of the request in your overrides
   of those methods. (I'm not sure about this. I might get rid of it in
   the next version.) Example::

     def my_view(request):
         ...
	 versioned_object, created = MyModel.objects.get_or_create(...)
	 versioned_object.save()
         versioned_object.export_to_repository(request, created)

   Both ``request`` and ``created`` are optional and default to None and
   False respectively. You can also pass a commit message and/or username
   to `export_to_repository` directly::

     versioned_object.export_to_repository(message="Foo", 
                                          username=request.user.username)

   The method will return the Revision of the commit, or None if there
   were no changes to apply.

You must provide one piece of configuration in your settings.py file:

* VCEXPORT_CHECKOUT_DIR: the absolute path to a local checkout of the
  repository that you want to store your data in

You will have to initialize your repository and checkout on your own.

You must have pysvn installed.

Originally developed at Columbia University's Center for New Media
Teaching & Learning <http://ccnmtl.columbia.edu>
