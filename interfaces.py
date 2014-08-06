# -*- coding: utf-8 -*-
"""
    interfaces
    ~~~~~~~~~~

    Implements a ``implements()`` function that does interfaces.  It's
    a very simple implementation and does not handle multiple calls
    to implements() properly.

    :copyright: (c) Copyright 2011 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
    
"""
    
#modify by jevnehuang 2014/8/6:
#Support attributes,add verify method,modify MRO stuff.

import sys


class Interface():
    __slots__ = ()
    
    
class Attribute(object):
    __slots__ = ()


def find_real_type(explicit, bases):
    if explicit is not None:
        return explicit
    for base in bases:
        if type(base) is not type:
            return type(base)
    return type


def iter_interface_members(interface):
    for key, value in interface.__dict__.iteritems():
        if callable(value) or isinstance(value,Attribute):
            yield key


def implemented(class_, interface, member):
    if callable(member):
        return getattr(class_, member).im_func \
            is not getattr(interface, member).im_func
    else:
        return member in class_.__dict__

def collect_interfaces(bases,interfaces):
    _interfaces=set()
    for base in bases:
        temp=getattr(base,'__interfaces__',[])
        _interfaces=_interfaces.union(set(temp))
    _interfaces=_interfaces.union(interfaces)
    return _interfaces
    
def make_meta_factory(metacls, interfaces):
    def __metaclass__(name, bases, d):
        real_type = find_real_type(metacls, bases)
        rv = real_type(name, bases, d)
        rv.__interfaces__=collect_interfaces(bases,interfaces)
        for interface in rv.__interfaces__:
            for member in iter_interface_members(interface):
                if not implemented(rv, interface, member):
                    raise NotImplementedError('Missing member %r on %r '
                        'from interface %r' % (member, rv.__name__,
                                               interface.__name__))
        return rv
    return __metaclass__


def implements(*interfaces):
    cls_scope = sys._getframe(1).f_locals
    print cls_scope
    metacls = cls_scope.get('__metaclass__')
    metafactory = make_meta_factory(metacls, interfaces)
    cls_scope['__metaclass__'] = metafactory

def verify(interface,target):
    _interfaces=getattr(target,'__interfaces__',[])
    return interface in _interfaces
        
    
if __name__ == '__main__':
    class IRenderable(Interface):
        x=Attribute()
        def render(self):
            raise NotImplementedError()
    
    class ITest(Interface):
        def test(self):
            """test"""
        
    class Base(object):
        implements(ITest)
        def test(self):
            pass
        
    class User(Base):
        implements(IRenderable)
        x=1
        def render(self):
            return self.username
        
        def test(self):
            pass

    print User.__bases__
    print User.__interfaces__
    print 'verify User:',verify(IRenderable,User)
    print 'verify User instance:',verify(IRenderable,User())
    print 'verify Attribute:',verify(IRenderable,Attribute)
    print 'verify interface of base:',verify(ITest,User)
