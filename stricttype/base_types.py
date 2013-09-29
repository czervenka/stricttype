import re
from types import StringTypes

from exceptions import ValidationError

__author__ = 'czervenka'

class StrictValue(object):

    def __init__(self, message, name, field_type, value=None):
        self._type = field_type
        self._message = message
        self._name = name
        self._value = None
        self._validated = False
        if value is not None:
            self.import_value(value)

    def import_value(self, value=None):
        try:
            self._value = self._type.import_value(value)
        except ValidationError, e:
            message = '%s: %s' % (self, e.message)
            raise ValidationError(self, message)
        else:
            self._validated = True

    def export_value(self):
        if not self._validated:
            raise ValueError('%s: %s' % (self, "Exporting non-initialized value."))
        return self._type.export_value(self._value)

    def as_dict(self):
        return self._type.as_dict(self._value)

    def __str__(self):
        return '%s.%s' % (self._message, self._name)


class StrictType(object):
    '''abstract message field'''

    def __init__(self, required=True, default=None, repeat_min=None, repeat_max=None):
        self._required = required
        self._default = None
        self._repeat_min = repeat_min
        self._repeat_max = repeat_max
        self._repeated = repeat_min is not None or repeat_max is not None

    def _export_one_value(self, value):
        return value

    def import_value(self, value):
        return self.validate(value)

    def export_value(self, value):
        if self._repeated and value is not None:
            return [self._export_one_value(v) for v in value]
        else:
            return self._export_one_value(value)

    def as_dict(self, value):
        return self.export_value(value)

    def _adapt(self, value):
        raise NotImplementedError()

    def _validate_one(self, value):
        '''validates value and returns it'''
        try:
            value = self._adapt(value)
        except (TypeError, ValueError), e:
            raise ValidationError(self, e.message)
        return value

    def validate(self, value):
        if value is None:
            if self._required:
                raise ValidationError(self, "Value is required.")
            else:
                return self._default
        elif self._repeated:
            values = [self._validate_one(v) for v in value]
            if self._repeat_min is not None and len(values) < self._repeat_min:
                raise ValidationError(self, "Value should be repeated at least %d x." % self._repeat_min)
            if self._repeat_max is not None and len(values) > self._repeat_max:
                raise ValidationError(self, "Value should be repeated at most %d x." % self._repeat_max)
            return values
        else:
            return self._validate_one(value)


class RangeType(StrictType):

    def __init__(self, min_value=None, max_value=None, required=True, default=None, repeat_min=None, repeat_max=None):
        self._min_value = min_value
        self._max_value = max_value
        super(RangeType, self).__init__(required, default, repeat_min, repeat_max)

    def _validate_one(self, value):
        min_val, max_val = self._min_value, self._max_value
        value = super(RangeType, self)._validate_one(value)
        if value is not None:
            if min_val is not None and value < min_val:
                raise ValidationError(self, "Value could not be lower than %r." % self._min_value)
            if max_val is not None and value > max_val:
                raise ValidationError(self, "Value could not be lower than %r." % self._max_value)
        return value


class IntegerType(RangeType):
    _adapt = int


class FloatType(RangeType):
    _adapt = float


class StringType(StrictType):

    def __init__(self, regexp=None, required=True, default=None, repeat_min=None, repeat_max=None):
        self._regexp = re.compile(regexp) if regexp else None
        super(StringType, self).__init__(required, default, repeat_min, repeat_max)

    def _adapt(self, value):
        return value if isinstance(value, StringTypes) else unicode(value)

    def _validate_one(self, value):
        value = super(StringType, self)._validate_one(value)
        regexp = self._regexp
        if value is not None and regexp is not None and not regexp.match(value):
            raise ValidationError(self, "Value does not match the expression %r." % regexp.pattern)
        return value
