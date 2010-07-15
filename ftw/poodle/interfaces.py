from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from izug.poodle import poodleMessageFactory as _

class IPoodle(Interface):
    """ A 'doodle'-like content type that helps finding a date for a meeting """

class IPoodleConfig(Interface):
    """ Adapter for annotation storage of poodledata """