#!/bin/python

import attrs
from baseclass import BaseClass

@attrs.define(frozen=True, kw_only=True, slots=False)
class NewClass(BaseClass):
	_id: int = BaseClass.comparable(1)
	_value: str = BaseClass.comparable(8, eq=str.lower)

@attrs.define(frozen=True, kw_only=True, slots=False)
class OtherClass(BaseClass):
	_id: int = BaseClass.comparable(4)
	_obj: NewClass = BaseClass.comparable(BaseClass.COMPARE_DEEP)

a=NewClass(id=1, value="Test String")
b=NewClass(id=1, value="test string")
c=OtherClass(id=2, obj=a)
d=OtherClass(id=2, obj=b)

ret=c.compare(d)
print(ret)

z=c.serialize()

print(type(z))
print(len(z))
print(z)

obj = BaseClass.deserialize(z)

ret=d.compare(obj)
print(ret)