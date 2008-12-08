from zope.interface import implements

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    from Products.Archetypes import atapi

from Products.ATContentTypes.content import base

from Products.ATContentTypes.content import schemata
from Products.CMFCore import permissions


from izug.poodle import poodleMessageFactory as _
from izug.poodle.interfaces import IPoodle
from izug.poodle.config import PROJECTNAME


PoodleSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
))

schemata.finalizeATCTSchema(PoodleSchema, moveDiscussion=False)


class Poodle(base.ATCTContent):
    """ A 'doodle'-like content type that helps in finding a date for a meeting """
    implements(IPoodle)

    portal_type = "Meeting poll"
    schema = PoodleSchema
    
atapi.registerType(Poodle, PROJECTNAME)