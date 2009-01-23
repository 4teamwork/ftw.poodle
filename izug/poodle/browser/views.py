from Products.Five.browser import BrowserView

from AccessControl import getSecurityManager  
from Products.CMFCore.utils import getToolByName  
from zope.component import getMultiAdapter, queryMultiAdapter 
from zope.component import queryUtility

from plone.i18n.normalizer.interfaces import IURLNormalizer

from izug.poodle import poodleMessageFactory as _
from izug.poodle.interfaces import IPoodle, IPoodleConfig

from plone.memoize import ram

def _get_poodle_results_key(method, self, data):
    return str(data)

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile,PageTemplateFile

class PoodleView(BrowserView):


    def getUserFullname(self, userid):
        mtool = getToolByName(self.context, "portal_membership") 
        return mtool.getMemberById(userid).getProperty('fullname')

    def saveData(self):
        if hasattr(self.context.REQUEST, 'form'):
            portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
            user = portal_state.member()
            form = self.context.REQUEST.form
            values = form.values()
            if values == ['']:
                return
            self.context.saveUserData(user.id, values)
            self.context.sendNotification(self.getUserFullname(user.id))
            
        
    def sendNotification(self, user):
        """Sends a notification after someone filled out the meeting poll"""
        mtool = getToolByName(self.context, "portal_membership") 
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        site_properties = getToolByName(self.context, 'portal_properties').site_properties
        
        host = getToolByName(self.context, "MailHost")
        creator = self.context.Creator() # send a mail to the creator of the poll
        send_to_address = mtool.getMemberById(creator).getProperty('email')
        if send_to_address == '': send_to_address = site_properties.email_from_address
        send_from_address = site_properties.email_from_address
        subject = u"%s %s" % (_(u"izugpoodle_mail_subject", default="Update on meeting poll at"), self.context.absolute_url())
        template = getattr(self.context, 'poodle_notification')
        encoding = portal.getProperty('email_charset')
        envelope_from = send_from_address
        # Cook from template
        message = template(self,  username=self.getUserFullname(user.id), url=self.context.absolute_url())
        result = host.secureSend(message, send_to_address,
                                 envelope_from, subject=subject,
                                 subtype='plain', charset=encoding,
                                 debug=False, From=send_from_address)

            #{'form.button.Save': 'Speichern', 'hamu2.12.2008': '2.12.2008', 'hamu13.7.82': '13.7.82'}
        
        

    def renderTable(self, context):
        view = getMultiAdapter((context, self.context.request), name=u'izug_poodle_table')
        return view()


class PoodleTableView(BrowserView):

    def isCurrentUser(self, userid):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        user = portal_state.member()
        return user.id == userid

    def getUserFullname(self, userid):
        mtool = getToolByName(self.context, "portal_membership") 
        return mtool.getMemberById(userid).getProperty('fullname')

    def getCssClass(self, data):
        if data == None: return "not_voted"
        elif data == True: return "positive"
        elif data == False: return "negative"

    def getInputId(self, user, date):
        date = date['date']
        return queryUtility(IURLNormalizer).normalize(user + date)

    @ram.cache(_get_poodle_results_key)
    def poodleResults(self,data=False):
        context = self.context.aq_inner
        if not data:
            data = context.getPoodleData()
        
        dates = data['dates']
        #remove the dates entry from list
        data_date_only = data.values()
        data_date_only.remove(dates)
        counted = []
        
        for base_d in dates:
            counter = 0
            for d in data_date_only:
                if d[base_d]:
                    counter += 1
            counted.append(counter)
                    
        #get highest value
        heightest = counted[:]
        heightest.sort()
        heightest.reverse()
        h_value = heightest[:1] and heightest[:1][0] or 0
        html_data = ''
        for v in counted:
            if v == h_value:
                v = "<b>%s</b>" % v
            html_data += "<td>%s</td>" % v
        return html_data


class JQSubmitData(BrowserView):
    def __call__(self):
        izug_poodle_view = getMultiAdapter((self.context, self.request), name=u'izug_poodle_view')
        
        #woke up archetype 10times
        #izug_poodle_view.saveData()
        
        # copied together, now we just once call the at object
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        user = portal_state.member()
        userid = user.id
        form = self.context.REQUEST.form
        dates = form.values()
        
        if dates == ['']:
            return 1

        poodledata = self.context.getPoodleData()
        if userid in poodledata.keys():
            for date in poodledata["dates"]:
                if date in dates:
                    poodledata[userid][date] = True
                else: 
                    poodledata[userid][date] = False
        #self.setPoodleData(poodledata)
        if IPoodle.providedBy(self):
            IPoodleConfig(self).setPoodleData(data)
        #XXX - use zope dict
        self.context.updatePoodleData()
            
        
        #send mail - XXX: send async by jquery (takes a lot of time)
        izug_poodle_view.sendNotification(user)
        
        #create journal entry
        journal_view = queryMultiAdapter((self.context, self.context.REQUEST), name="journal_action")
        if journal_view is None:
            return 1
        comment = 'Der Benutzer %s hat an der Umfrage (%s) teilgenommen' % (user.get('fullname', ''),self.context.Title())
        journal_view.addJournalEntry(self.context,comment)
        
        return 1
        
