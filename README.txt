This package provides some basic utilities for backing up django model
instances to a version-controlled repository. It is very experimental
at this point and hasn't been tested in any meaningful environment.

It does not provide any utilities for restoring live data from backups.

How it works
============

There is an application-level API and a model-level API.

Use the model-level API to define export behavior per model class, with
automatic exports on save.

Use the application-level API to define export behavior in views (for
example) and explicitly trigger content export from your own code.

The model-level API
-------------------

The design is inspired by Django's ModelAdmin and ModelForm aspect-oriented
pattern. The core behaviors are defined in the `vcexport.models.Exporter`
class, which is analogous to ModelAdmin. Like ModelAdmin and ModelForm, you 
will subclass the default base to customize the behavior on a per-model basis.

1. For automatic versioning of models, register them with vcexport::

     import vcexport
     vcexport.register(MyModel)

   This will connect a post_save signal.

2. You can customize the export behavior on a per-model basis by subclassing
   `vcexport.models.Exporter` and telling vcexport to register your model with
   the custom Exporter:

     class MyExporter(vcexport.models.Exporter):
       ...
     vcexport.register(MyModel, exporter=MyExporter)

3. By default, models are serialized to django's XML format, because it
   works well with `diff` and is generic.

4. You can customize the serialization per model by passing a custom
   template path as a class attribute::
    
     class MyExporter(Exporter):
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

     class MyExporter(Exporter):
         def repository_path(self):
     	     return '/my_custom/path_for/this_model/' + self.object.color

   Note that if you do this, you may end up with multiple model instances
   that save to the same file path in the repository. This is a feature.

6. The default committing user is undefined. At present you cannot
   customize this.

   The default commit message is uninteresting: "Object {{instance.pk}}
   (from '{{app_name}}.{{model_name}}') saved by django-vcexport."

   You can customize the commit message with a model method that
   takes a boolean ``created``, and returns a string::

     class MyExporter(Exporter):
         def repository_commit_message(self, created):
             if created:
                 return "User %s committed a new %s" % (
 		   self.object.user.username, self.object.color)
             return "User %s committed %s" % (self.object.user.username, 
	     	    	     	       	      self.object.color)

The application-level API
-------------------------

You can also export the content explicitly, for example in your model's
`save()` method, in view code, etc, with the `vcexport.export_to_repository`
function::

  def my_view(request):
      ...
      object = MyModel.objects.get(...)
      object.morx = request.POST['new_morx']
      object.save()

      import vcexport
      vcexport.export_to_repository(object)

The default template, commit message, etc are the same as with the model API.
You can customize them in your own code and pass them to `export_to_repository`::

  def my_view(request):
      ...
      object, created = MyModel.objects.get_or_create(...)
      object.morx = request.POST['new_morx']
      object.save()

      import vcexport
      vcexport.export_to_repository(
                 object, created=created,
                 repository_template='/fleem/morx.html',
                 message="Changed the morx",
                 repository_path='/fleem/objects/%s' % object.pk)

The `export_to_repository` function will return the Revision of the commit,
or None if there were no changes to commit.   

Configuration
=============

You must provide one piece of configuration in your settings.py file:

* VCEXPORT_CHECKOUT_DIR: the absolute path to a local checkout of the
  repository that you want to store your data in

You will have to initialize your repository and checkout on your own.

To use with Subversion, you must have pysvn installed.


Originally developed at Columbia University's Center for New Media
Teaching & Learning <http://ccnmtl.columbia.edu>
