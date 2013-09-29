# coding=utf-8
from unittest import TestCase
import stricttype
from stricttype import base_types, message
from nose.util import odict


class MyMessageType(stricttype.Message):
    val = stricttype.StringType()

class MyMessage(stricttype.Message):

    i = stricttype.IntegerType(min_value=1, max_value=10, required=False)
    s = stricttype.StringType(regexp='\d\d-\d\d-\d\d', required=False)
    m = stricttype.MessageType(MyMessageType, required=False)
    r = stricttype.IntegerType(repeat_min=1, repeat_max=2, required=False)


class TestMyApplication(TestCase):
    '''Test class description'''

    def test_message(self):
        '''Message'''

        msg = MyMessage(i=1, s='12-34-56')

        self.assertTrue(isinstance(msg, message.MessageInstance), 'Message instance is instance of MessageInstance')
        self.assertTrue(isinstance(msg._properties['i'], base_types.StrictValue), 'Test is of valid property.')
        'as_dict returns proper values'
        self.assertEqual(msg.as_dict(), {'i': 1, 's': '12-34-56', 'm': None, 'r': None})
        'setting tuple to IntegerType raises ValidationError'
        self.assertRaises(stricttype.ValidationError, MyMessage, i=tuple())
        'setting value lower than `min_value` raises ValidationError'
        self.assertRaises(stricttype.ValidationError, MyMessage, i=0)
        'setting value higher than `max_value` raises ValidationError'
        self.assertRaises(stricttype.ValidationError, MyMessage, i=11)
        'setting string that does not match regular expression raises ValidationError'
        self.assertRaises(stricttype.ValidationError, MyMessage, s='123456')

    def test_bare_class(self):
        'bare StrictType is not usable'
        class MyMessage(stricttype.Message):
            t = stricttype.StrictType()
        self.assertRaises(NotImplementedError, MyMessage, t=1)

    def test_messagefield(self):
        '''MessageType'''

        msg_f = MyMessageType(val='test')
        msg = MyMessage(m=msg_f)

        class WrongMessageType(stricttype.Message):
            pass
        'message field retrieved as property is the same as the value in constructor'
        self.assertEquals(msg.m, msg_f)
        'MessageType accepts only instances not class itself'
        self.assertRaises(stricttype.ValidationError, MyMessage, m=MyMessageType)
        'setting different class raises ValidationError'
        self.assertRaises(stricttype.ValidationError, MyMessage, m=WrongMessageType())

    def test_dict(self):
        '''Exported dict matches imported one'''

        data = {
            'i' : 1,
            's' : '11-11-11',
            'm' : {
                'val': 'hokud pokus',
            },
            'r' : [ 1, ],
        }

        self.assertEquals(MyMessage(**data).as_dict(), data)

    def test_repeated_field(self):
        '''Type - repeat_min / repeat_max'''

        msg = MyMessage(r=[1, 2])

        'repeated type returns the same list as got in construcotr'
        self.assertEquals(msg.r, [1, 2])
        'raises exception for repeat_max is 2'
        self.assertRaises(stricttype.ValidationError, MyMessage, r=[1, 2, 3])
        'raises exception for repeat_min is 1'
        self.assertRaises(stricttype.ValidationError, MyMessage, r=[])
        'does not raise exception (required is not set)'
        self.assertIsNone(MyMessage(r=None).r)

    def test_invalid_property(self):
        '''Message - invalid property names'''

        class MyMessage(stricttype.Message):
            as_dict = stricttype.StringType(required=False)
        'as_dict is invalid name for message field'
        self.assertRaises(ValueError, MyMessage)

        class MyMessage(stricttype.Message):
            _invalid_property = stricttype.StringType(required=False)
        'property starting with underscore is not valid property name'
        self.assertRaises(ValueError, MyMessage)

    def test_required(self):
        '''Message - required'''

        'creating message without values for required fields raises exception'
        self.assertRaises(stricttype.ValidationError, MyMessageType)

    def test_can_inherit(self):
        '''Message is inheritable'''
        class Ma(stricttype.Message):
            id = stricttype.IntegerType()

        class Mb(Ma):
            name = stricttype.StringType()

        'Message classes can be extended by inheritance'
        self.assertEqual(Mb(id=1, name='test Mb').as_dict(), {'id': 1, 'name': 'test Mb'})

    def test_string_type(self):
        '''String returns what it gets'''
        class StrMessage(stricttype.Message):
            s = stricttype.StringType()

        msg = StrMessage(s='abc')
        'StringType returns string if filled by string'
        self.assertEqual(msg.s, 'abc')

        s=u'říšžľťóčýůňúďáé'
        msg = StrMessage(s=s)
        'StringType returns unicode if filled by unicode (and works with utf-8 chars)'
        self.assertEqual(msg.s, s)

        msg = StrMessage(s=1)
        'StringType converts non-string types to unicode if possible'
        self.assertEqual(msg.s, u'1')

    def test_attribute_error(self):
        'message returns values as properties'

        m = MyMessage()
        'getting nonexisting property raises attribute error'
        self.assertRaises(AttributeError, getattr, m, 'not_a_property')

        'setting nonexisting property raises attribute error'
        self.assertRaises(AttributeError, setattr, m, 'not_a_property', 'abc')

        'setting property needs proper value'
        self.assertRaises(stricttype.ValidationError, setattr, m, 'i', 's')

        'hasattr'
        self.assertTrue(m.__hasattr__('i'))
        self.assertFalse(hasattr(m, 'not_a_property'))
        self.assertTrue(hasattr(m, 'as_dict'))

        'setattr'
        m.i = 1
        self.assertEquals(m.i, 1)
        del m.i
        self.assertEquals(m.i, None)

        m = MyMessageType(val='abc')

        self.assertRaises(stricttype.ValidationError, delattr, m, 'val')



class TestInternals(TestCase):

    def test_strict_value_can_be_empty(self):
        message = stricttype.Message()
        v = stricttype.StrictValue(message, 'test', stricttype.StringType())
        self.assertRaises(ValueError, v.export_value)

    def test_message_encoder(self):
        class MyObj(object):
            def as_dict(self):
                return {'x': 1}

        'dumps exports dict from objects implementing `as_dict` method'
        self.assertEquals(str(stricttype.dumps(MyObj())), '{"x": 1}')

        'dumps result can be converted to unicode'
        self.assertEquals(unicode(stricttype.dumps(MyObj())), u'{"x": 1}')

        'dumps raises TypeError for object which could not handle'
        self.assertRaises(TypeError, str, stricttype.dumps(object()))

        m = MyMessageType(val='abc')
        self.assertEquals(m.as_dict(), m._dict_value)
        m.val = 'cba'
        'as_dict cache is reset after changing a value'
        self.assertIsNone(getattr(m, '_dict_value', None))
