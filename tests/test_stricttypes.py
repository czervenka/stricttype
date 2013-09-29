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
        # should be fine
        self.assertEqual(msg.as_dict(), {'i': 1, 's': '12-34-56', 'm': None, 'r': None})
        # exception for tuple is not int
        self.assertRaises(stricttype.ValidationError, MyMessage, i=tuple())
        # exception for min_value is 1
        self.assertRaises(stricttype.ValidationError, MyMessage, i=0)
        # exception for max_value is 10
        self.assertRaises(stricttype.ValidationError, MyMessage, i=11)
        # exception for string does not conform to regex
        self.assertRaises(stricttype.ValidationError, MyMessage, s='123456')

    def test_messagefield(self):
        '''MessageType'''

        msg_f = MyMessageType(val='test')
        msg = MyMessage(m=msg_f)

        class WrongMessageType(stricttype.Message):
            pass
        # this should be ok
        print 'c: ' + msg.m.__class__.__name__
        self.assertEquals(msg.m, msg_f)
        # raises exception for the value is class (not an instance)
        self.assertRaises(stricttype.ValidationError, MyMessage, m=MyMessageType)
        # raises exception for WrongMessageType is not the message class set
        # in definition
        self.assertRaises(stricttype.ValidationError, MyMessage, m=WrongMessageType())

    def test_dict(self):

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

        self.assertEquals(msg.r, [1, 2])
        # raises exception for repeat_max is 2
        self.assertRaises(stricttype.ValidationError, MyMessage, r=[1, 2, 3])
        # raises exception for repeat_min is 1
        self.assertRaises(stricttype.ValidationError, MyMessage, r=[])
        # does not raise exception (required is not set)
        self.assertIsNone(MyMessage(r=None).r)

    def test_invalid_property(self):
        '''Message - invalid property names'''

        class MyMessage(stricttype.Message):
            as_dict = stricttype.StringType(required=False)
        self.assertRaises(ValueError, MyMessage)

        class MyMessage(stricttype.Message):
            _invalid_property = stricttype.StringType(required=False)
        self.assertRaises(ValueError, MyMessage)

    def test_required(self):
        '''Message - required'''

        self.assertRaises(stricttype.ValidationError, MyMessageType)

    def test_can_inherit(self):
        '''Message is inheritable'''
        class Ma(stricttype.Message):
            id = stricttype.IntegerType()

        class Mb(Ma):
            name = stricttype.StringType()

        self.assertEqual(Mb(id=1, name='test Mb').as_dict(), {'id': 1, 'name': 'test Mb'})

    def test_string_type(self):
        '''String returns what it gets'''
        class StrMessage(stricttype.Message):
            s = stricttype.StringType()

        msg = StrMessage(s='abc')
        self.assertEqual(msg.s, 'abc')

        msg = StrMessage(s=u'abc')
        self.assertEqual(msg.s, u'abc')

        msg = StrMessage(s=1)
        self.assertEqual(msg.s, u'1')

