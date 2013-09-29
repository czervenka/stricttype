import json
from base_types import StrictType, StrictValue
from exceptions import ValidationError


class MessageEncoder(json.JSONEncoder):

    def default(self, o):
        if hasattr(o, 'as_dict'):
            return o.as_dict()
        else:
            super(MessageEncoder, self).default(o)

class dumps(object):

    def __init__(self, data):
        self._data = data

    def __str__(self):
        return self._dumps()

    def __unicode__(self):
        return unicode(self._dumps())

    def _dumps(self):
        return json.dumps(self._data, cls=MessageEncoder)



class MessageInstance(object):
    '''Implements restapi message class'''

    def __init__(self, message, data):
        self.__dict__['_type'] = message
        self.__dict__['_properties'] = self._gather_properties(message)
        self._import_data(data)

    def _import_data(self, data):
        for prop_name, field in self._properties.items():
            setattr(self, prop_name, data.get(prop_name, None))

    def __getattr__(self, key):
        if key in self._properties:
            return self._properties[key].export_value()
        else:
            raise AttributeError("%s has no attributte %s." % (self.__class__, key))

    def __setattr__(self, key, value):
        if key in self.__dict__['_properties']:
            self.__dict__['_properties'][key].import_value(value)
            self._on_change()
        else:
            raise AttributeError("%s has no attributte %s." % (self.__class__, key))

    def __hasattr__(self, key):
        return key in self.__dict__ or key in self.__dict__['_properties']

    def __delattr__(self, key):
        if key in self.__dict__:
            del self.__dict__[key]
        elif key in self.__dict__['_properties']:
            setattr(self, key, None)
        else:
            raise AttributeError("%s has no attributte %s." % (self.__class__, key))

    def _on_change(self):
        if hasattr(self, '_dict_value'):
            del self._dict_value

    def as_dict(self):
        if not hasattr(self.__dict__, '_dict_value'):
            ret = {}
            for prop_name, value in self._properties.items():
                if hasattr(value, 'as_dict'):
                    ret[prop_name] = value.as_dict()
                else:
                    ret[prop_name] = value.export_value()
            self.__dict__['_dict_value'] = ret
        return self._dict_value

    def __repr__(self):
        return 'M'+repr(self.as_dict())

    def _gather_properties(self, message):
        ret = {}
        for base in message.__bases__:
            ret.update(self._gather_properties(base))
        for key, field_def in message.__dict__.items():
            if isinstance(field_def, StrictType):
                if key == 'as_dict' or key.startswith('_'):
                    raise ValueError("Invalid property name %s." % key)
                ret[key] = StrictValue(self, key, field_def)
        return ret

    def __str__(self):
        return self._type.__name__


class Message(object):

    def __new__(cls, **data):
        return MessageInstance(cls, data)


class MessageType(StrictType):

    def __init__(self, field_class, required=True, default=None, repeat_min=None, repeat_max=None):
        if not issubclass(field_class, Message):
            raise TypeError("field_class must be a Message or derived bu is %r." % field_class)
        self._field_class = field_class
        super(MessageType, self).__init__(required, default, repeat_min=repeat_min, repeat_max=repeat_max)

    def _adapt(self, value):
        if value is None:
            return value
        elif isinstance(value, MessageInstance):
            return value
        elif isinstance(value, dict):
            return self._field_class(**value)
        else:
            raise ValidationError(self, "Could not convert value of type %r to %r." % (value.__class__.__name__, self._field_class.__name__))

    def _validate_one(self, value):
        value = super(MessageType, self)._validate_one(value)
        if value is None:
            return value
        elif value._type != self._field_class:
            raise ValidationError(self, "Value should be of type %r but is %r." % (self._field_class, value._type))
        elif not isinstance(value, MessageInstance):
            raise ValidationError(self, "Value should be of type %r but is %r." % (self._field_class, value._type))
        else:
            return value

    def as_dict(self, value):
        value = self.export_value(value)
        if value is None:
            return None
        elif self._repeated and value is not None:
            return [ val.as_dict() for val in value ]
        else:
            return value.as_dict()

    def _export_one_value(self, value):
        if value is None:
            return None
        else:
            return value
