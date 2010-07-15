from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations
from interfaces import IPoodle, IPoodleVotes
from persistent.mapping import PersistentMapping

class PoodleVotes(object):
    implements(IPoodleVotes)
    adapts(IPoodle)
    
    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)
    
    def getPoodleData(self):
        return self.annotations.get('poodledata', PersistentMapping())
    
    def setPoodleData(self, data):
        if data:
            self.annotations['poodledata'] = PersistentMapping(data)
            

    
