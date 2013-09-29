
What is it?
===========
StrictType is validation library useful when building an interface. It was
originally written for restapi (json rest request handler) to allow validating
json messages.

It's usage is close to Google's endpoint Message.

... and also, this is my first library with 100% test coverage :)


Example
-------

.. code:: python

   from stricttype import Message, StringType, IntegerType, MessageType

   class Person(Message):
        
        email = StringType(regexp=r'\w+@\w+\.\w{2,3}')  # example only (not a good way to validate e-mail)
        name = StringType()
        phone = StringType(regexp=r'\d{9}', required=False)
        door_num = IntegerType(min_value=0, max_value=550, required=False)

        @property
        def full_email(self):
            return '%s <%s>' % (self.name, self.email)

   class Boss(Person):
        
        employes = MessageType(Person, repeat_min=1)

    data = {
        'email': 'the.boss@example.com',
        'name': 'Bossowitzsh',

        'employees': [
            {'email': 'john.brown@example.com'},
            {'email': 'petter@example.com', 'name': 'Petter Blake', phone='999999999', door_num=10},
        ]
    }
    boss = Boss(data)
    >>> ValidationError("Person.name: Value is required")
    data['employees'][0]['name'] = 'James Brown'
    boss = Boss(data)  # validated now
    boss.email
    >>> 'the.boss@example.com'
    from stristtype import dumps
    dumps(boss.employees[0])
    >>> '{"email": "john.brown@example.com", "name": "James Brown"}
    boss.full_email
    >>> 'Bossowitzsh <the.boss@example.com>'


What is still missing?
----------------------

- export of the definition (xml, json)
- xml representation
- BooleanType
- other basic types (ie. EmailType, DatetimeType, DateType)


