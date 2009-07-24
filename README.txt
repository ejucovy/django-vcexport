This package provides some basic utilities for backing up django model instances
to a Subversion repository. It is very experimental at this point and hasn't been
tested in any meaningful environment.

It does not provide any utilities for restoring live data from backups, though
it may one day.

Two distinct use cases are supported:
* You want to version a model wholesale
* You have a model which has one or two document-like text fields, and you want to
  version those fields only

To use the former, you should subclass svndjango.models.SubversionedMixin and call
its .save method from your own. svndjango.models.SubversionedModel is an example
(which you can also just subclass directly and not worry about any of it, but it
lacks flexibility) -- you probably want to call SubversionedMixin.save only after
the "actual" .save to your RDB; this will ensure that you don't accidentally save
a revision that ends up being rolled back in the RDB.

Your model instances will be serialized to JSON and saved in repository paths that
look like `/module/name/class/name/instance_pk`.

To use the latter, your model should subclass svndjango.models.SVNDoc in the same
manner. Text fields to be versioned must be declared explicitly, by using the
svndjango.models.SubversionedTextField field instead of the standard TextField.

Your text fields will be saved directly into the repository in repository paths
that look like `/module/name/class/name/instance_pk/field_name`.

You must provide one piece of configuration in your settings.py file:
* SVNDJANGO_CHECKOUT_DIR: the absolute path to a local checkout of the repository
  that you want to store your data in

A second optional setting is supported:
* SVNDJANGO_SILENT_FAILURES: if this is set to True, then any exceptions caused
  by svndjango will be swallowed. This may be useful if you'd rather avoid user
  errors than preserve a strictly full history of changes.

You will have to initialize your SVN repository and checkout on your own, though
these may be automated in future versions. (Not that it's hard to do anyway)

You must have pysvn installed.
