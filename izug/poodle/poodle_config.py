from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations
from interfaces import IPoodle, IPoodleConfig

class PoodleConfig(object):
    implements(IPoodleConfig)
    adapts(IPoodle)
    
    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)
    
    def getPoodleData(self):
        return self.annotations.get('poodledata', {})
    
    def setPoodleData(self, data):
        if data:
            self.annotations['poodledata'] = data
            

    def getMeetingDate(self.context):
        return self.annotations.get('meetingdate','')
    def setMeetingDate(self,data):
        if data:
            self.annotatations['meetingdate'] = data
    
    meeting_date = property(getMeetingDate, setMeetingDate)

        
    
