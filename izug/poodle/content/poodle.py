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

from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column


from izug.poodle.datagridextension.CalendarColumn import CalendarColumn
from izug.poodle import poodleMessageFactory as _
from izug.poodle.interfaces import IPoodle, IPoodleConfig
from izug.poodle.config import PROJECTNAME

PoodleSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
    atapi.LinesField(
        name='users',
        vocabulary="getPossibleUsers",
        widget=atapi.InAndOutWidget
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
            label_msgid='izugpoodle_label_dates',
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

    security.declarePrivate("getPossibleUsers")
    def getPossibleUsers(self):
        pas, mtool = getToolByName(self, "acl_users"), getToolByName(self, "portal_membership") 
        result = []
        userids = []
        [userids.append(u['userid']) for u in pas.searchUsers() if u['userid'] not in userids]
        userids.sort()
        for userid in userids:
            user = mtool.getMemberById(userid) 
            result.append((userid, user.getProperty('fullname')))
        return result
            
#    def setDatesForUser(user, dates):
#        if user not in self.getUsers() or len(self.poodledata[user]) > 0: 
#            return False # user not allowed to vote or already voted
#        self.poodledata[user] = dates
#        return 
    def getPoodleData(self):
        if IPoodle.providedBy(self):
            return IPoodleConfig(self).getPoodleData()
        return {}
    
    def setPoodleData(self, data):
        if IPoodle.providedBy(self):
            IPoodleConfig(self).setPoodleData(data)

        
    def updatePoodleData(self):
        poodledata = self.getPoodleData()
        poodledata = self.updateDates(poodledata)
        poodledata = self.updateUsers(poodledata)
        self.setPoodleData(poodledata)
        self.updateSharing()
        
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

    def updateDates(self, poodledata):
        dates = self.getDates()
        poodledata["dates"] = [i['date'] for i in dates]
        return poodledata
        
    def updateUsers(self, poodledata):
        users = self.getUsers()
        dates = [i['date'] for i in self.getDates()]
        for user in users:
            if user not in poodledata.keys():
                # add user to data and fill dates with None
                userdates = {}
                [userdates.setdefault(date) for date in dates]
                poodledata[user] = userdates                    
            else:
                # check if the dates are correct
                userdates = poodledata[user]
                for date in dates:
                    if date not in userdates.keys():
                        # a new date
                        userdates[date] = None
        # check if we need to remove any users from poodledata
        for user in poodledata.keys():
            if user != 'dates' and user not in users:
                del(poodledata[user])
        return poodledata
    
    def saveUserData(self, userid, dates):
        poodledata = self.getPoodleData()
        if userid in poodledata.keys():
            for date in poodledata["dates"]:
                if date in dates:
                    poodledata[userid][date] = True
                else: 
                    poodledata[userid][date] = False
        self.setPoodleData(poodledata)
    
    
atapi.registerType(Poodle, PROJECTNAME)