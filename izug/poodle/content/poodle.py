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
from zope.component import getMultiAdapter, queryMultiAdapter, queryUtility
from izug.arbeitsraum.interfaces import IArbeitsraumUtils

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
        allow_empty_rows = False,
        widget=DataGridWidget(
            auto_insert = True,  
            columns= {"date": Column(_(u"izugpoodle_desc_date", default="Date (TT. MM. JJJJ)")), "duration": Column(_(u"izugpoodle_desc_duration", default="Time / Duration"))},
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
        """Collect users with a given role and return them in a list.
        """
        pas_tool = getToolByName(self, 'acl_users')
        a_util = queryUtility(IArbeitsraumUtils,name="arbeitsraum-utils")
        if not a_util:
            return (atapi.DisplayList())
        users = a_util.getAssignableUsers(self,'Reader')
        results = []
        for u in users:
            user = pas_tool.getUserById(u[0])
            results.append((u[0], user.getProperty('fullname','')))
        return results
            
#    def setDatesForUser(user, dates):
#        if user not in self.getUsers() or len(self.poodledata[user]) > 0: 
#            return False # user not allowed to vote or already voted
#        self.poodledata[user] = dates
#        return 

    security.declarePrivate("getPoodleData")
    def getPoodleData(self):
        if IPoodle.providedBy(self):
            return IPoodleConfig(self).getPoodleData()
        return {}
    
    security.declarePrivate("setPoodleData")
    def setPoodleData(self, data):
        if IPoodle.providedBy(self):
            IPoodleConfig(self).setPoodleData(data)

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
        return poodledata
        
    security.declarePrivate("updateUsers")
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

    security.declarePrivate("sendNotification")    
    def sendNotification(self, user):
        """Sends a notification after someone filled out the meeting poll"""
        mtool = getToolByName(self, "portal_membership") 
        portal = getToolByName(self, 'portal_url').getPortalObject()
        site_properties = getToolByName(self, 'portal_properties').site_properties
        
        host = getToolByName(self, "MailHost")
        creator = self.Creator() # send a mail to the creator of the poll
        send_to_address = mtool.getMemberById(creator).getProperty('email')
        if send_to_address == '': send_to_address = site_properties.email_from_address
        send_from_address = site_properties.email_from_address
        # XXX: translation not working!
        #subject = u"%s %s" % (_(u"izugpoodle_mail_subject", default="Update on meeting poll at"), self.absolute_url())
        subject = u"%s %s" % ("Update der Sitzungsumfrage unter", self.absolute_url())

        template = getattr(self, 'poodle_notification')
        encoding = portal.getProperty('email_charset')
        envelope_from = send_from_address
        # Cook from template
        message = template(self,  username=user, url=self.absolute_url())
        result = host.secureSend(message, send_to_address,
                                 envelope_from, subject=subject,
                                 subtype='plain', charset=encoding,
                                 debug=False, From=send_from_address)    

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
