from zope.interface import implements
from zope import schema, component

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    from Products.Archetypes import atapi

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import base

from Products.ATContentTypes.content import schemata
from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column
from ftw.poodle import poodleMessageFactory as _
from ftw.poodle.interfaces import IPoodle, IPoodleVotes
from ftw.poodle.config import PROJECTNAME

from Products.AutocompleteWidget import AutocompleteWidget

PoodleSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
    atapi.LinesField(
        name='users',
        vocabulary_factory="ftw.poodle.users",
        enforceVocabulary=True,
        widget=atapi.InAndOutWidget
        (
            label=_(u'ftwpoodle_label_users', default=u'Users'),
            actb_expand_onfocus=1,
        ),
        required=1,
        multivalued=1
    ),

    DataGridField(
        name='dates',
        allow_empty_rows = False,
        widget=DataGridWidget(
            auto_insert = True,  
            columns= {"date": Column(_(u"ftwpoodle_desc_date", default="Date (TT. MM. JJJJ)")), "duration": Column(_(u"ftwpoodle_desc_duration", default="Time / Duration"))},
            label=_(u'ftwpoodle_label_dates', default=u'Dates'),
        ),
        columns= ("date", "duration")
    ),
))

schemata.finalizeATCTSchema(PoodleSchema, moveDiscussion=False)


class Poodle(base.ATCTContent):
    """ A 'doodle'-like content type that helps finding a date for a meeting """
    implements(IPoodle)
    
    security = ClassSecurityInfo()
    
    portal_type = "Meeting poll"
    schema = PoodleSchema

    def get_users(self):
        factory = component.getUtility(schema.interfaces.IVocabularyFactory, name='ftw.poodle.users', context=self)
        return [t.value for t in factory(self)]
        

    security.declarePrivate("getDatesHash")
    def getAviableChoices(self):
        return [str(hash('%s%s' % (a['date'],a['duration']))) for a in self.getDates()]

    security.declarePrivate("getPoodleData")
    def getPoodleData(self):
        if IPoodle.providedBy(self):
            return IPoodleVotes(self).getPoodleData()
        return {}
    
    security.declarePrivate("setPoodleData")
    def setPoodleData(self, data):
        if IPoodle.providedBy(self):
            IPoodleVotes(self).setPoodleData(data)

    security.declarePrivate("updatePoodleData")        
    def updatePoodleData(self):
        poodledata = self.getPoodleData()
        poodledata = self.updateDates(poodledata)
        poodledata = self.updateUsers(poodledata)
        self.setPoodleData(poodledata)
        self.updateSharing()
        
    security.declarePrivate("updateSharing")
    def updateSharing(self):
        """ 
        Allow the selected Users to view the object
        """
        users = self.getUsers()
        wanted_roles = [u'Reader',]
        for user in users:
            self.manage_setLocalRoles(user, wanted_roles)
        self.reindexObjectSecurity()
        # XXX: remove users?

    security.declarePrivate("updateDates")
    def updateDates(self, poodledata):
        dates = self.getDates()
        poodledata["dates"] = [i['date'] for i in dates]
        poodledata['ids'] = self.getAviableChoices()
        return poodledata
        
    security.declarePrivate("updateUsers")
    def updateUsers(self, poodledata):
        users = self.getUsers()
        choices = poodledata['ids']
        for user in users:
            if user not in poodledata.keys():
                # add user to data and fill dates with None
                userdates = {}
                [userdates.setdefault(choice) for choice in choices]
                poodledata[user] = userdates                    
            else:
                # check if the dates are correct
                userdates = poodledata[user]
                for choice in choices:
                    if choice not in userdates.keys():
                        # a new date
                        userdates[choice] = None
        # check if we need to remove any users from poodledata
        for user in poodledata.keys():
            if user not in ['dates', 'ids'] and user not in users:
                del(poodledata[user])
        return poodledata
    
    security.declarePrivate("saveUserData")
    def saveUserData(self, userid, dates):
        poodledata = self.getPoodleData()
        if userid in poodledata.keys():
            for date in poodledata["dates"]:
                if date in dates:
                    poodledata[userid][date] = True
                else: 
                    poodledata[userid][date] = False
        self.setPoodleData(poodledata)



    security.declarePrivate("getStats") 
    def getStats(self):
        data = self.getPoodleData()
        dates = data.get('dates')
        users = [u for u in data.keys() if u != 'dates']
        result = {}
        for date in dates:
            result[date] = 0
        for user in users:
            for date in data[user]: 
                if date == True: result[date] += 1
            
        return result
            
        
atapi.registerType(Poodle, PROJECTNAME)
