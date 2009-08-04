def deserialize(uri, contents, msg, kind, revs):
    from django.core import serializers

    object = serializers.deserialize('json', contents)[0]
    
    object.save()

# use with sven as
# x = SvnAccessEventEmitter()
# x.add_event_listener(deserialize)

