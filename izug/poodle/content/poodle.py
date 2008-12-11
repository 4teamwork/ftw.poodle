from zope.interface import implements

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    from Products.Archetypes import atapi

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import base

from Products.ATContentTypes.content import schemata
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from Products.AddRemoveWidget import AddRemoveWidget
from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column


from izug.poodle.datagridextension.CalendarColumn import CalendarColumn
from izug.poodle import poodleMessageFactory as _
from izug.poodle.interfaces import IPoodle
from izug.poodle.config import PROJECTNAME

PoodleSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
    atapi.LinesField(
        name='users',
        vocabulary="getPossibleUsers",
        widget=AddRemoveWidget
        (
            label="Users",
            label_msgid='izugpoodle_label_users',
            i18n_domain='izugpoodle',
        ),
        required=1,
        multivalued=1
    ),

    DataGridField(
        name='dates',
        widget=DataGridWidget(
            columns= {"date": Column("Date (TT. MM. JJJJ)"), "duration": Column("Time / Duration")},
            label='Dates',
            label_msgid='izugpoodle_label_users',
            i18n_domain='izugpoodle',
        ),
        columns= ("date", "duration")
    ),
    
    # XXX: Ein Datumsfeld waere schoen; wird von Datagridfield noch nicht unterstuetzt, deshalb habe ich selber mit "CalendarColumn" angefangen.
    # Funktioniert leider noch nicht. So wuerde es gehen:
    #
    # DataGridField(
    #     name='dates',
    #     widget=DataGridWidget(
    #         columns= {"date": CalendarColumn("Date"), },
    #         label='Dates',
    #         label_msgid='izugpoodle_label_users',
    #         i18n_domain='izugpoodle',
    #     ),
    #     columns= ("date",)
    # ),
))

schemata.finalizeATCTSchema(PoodleSchema, moveDiscussion=False)


class Poodle(base.ATCTContent):
    """ A 'doodle'-like content type that helps finding a date for a meeting """
    implements(IPoodle)
    
    security = ClassSecurityInfo()
    
    portal_type = "Meeting poll"
    schema = PoodleSchema
    
    #data format:
    #data = { "dates": ["1.1.", "1.2"],
    #         "user1": {"1.1.": True, "1.2": False},
    #         "user2": {"1.1.": None, "1.2": None}, }
    
    _poodledata = {}
    
    security.declarePublic("getPoodleData")    
    def getPoodleData(self):
        return self._poodledata
        
    def updatePoodleData(self):
        self.updateDates()
        self.updateUsers()
        
    security.declarePrivate("updateDates")
    def updateDates(self):
        dates = self.getDates()
        self._poodledata["dates"] = [i['date'] for i in dates]
        
    security.declarePrivate("updateUsers")    
    def updateUsers(self):
        users = self.getUsers()
        dates = [i['date'] for i in self.getDates()]
        for user in users:
            if user not in self._poodledata.keys():
                # add user to data and fill dates with None
                userdates = {}
                [userdates.setdefault(date) for date in dates]
                self._poodledata[user] = userdates                    
            else:
                # check if the dates are correct
                userdates = self._poodledata[user]
                for date in dates:
                    if date not in userdates.keys():
                        # a new date
                        userdates[date] = None
        # check if we need to remove any users from poodledata
        for user in self._poodledata.keys():
            if user not in users:
                del(self._poodledata[user])
                
            
    security.declarePrivate("getPossibleUsers")
    def getPossibleUsers(self):
        pas, mtool = getToolByName(self, "acl_users"), getToolByName(self, "portal_membership") 
        result = []
        userids = [u['userid'] for u in pas.searchUsers()]
        userids.sort()
        
        for userid in userids:
            user = mtool.getMemberById(userid) 
            result.append((userid, user.getProperty('fullname')))
        return result
            
    def setDatesForUser(user, dates):
        if user not in self.getUsers() or len(self.poodledata[user]) > 0: 
            return False # user not allowed to vote or already voted
        self.poodledata[user] = dates
        return 
    
    
atapi.registerType(Poodle, PROJECTNAME)