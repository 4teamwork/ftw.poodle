from Products.Five.browser import BrowserView

from AccessControl import getSecurityManager  
from Products.CMFCore.utils import getToolByName  
from zope.component import getMultiAdapter, queryMultiAdapter 
from zope.component import queryUtility
from zope.app.pagetemplate import ViewPageTemplateFile

from plone.i18n.normalizer.interfaces import IURLNormalizer

from izug.poodle import poodleMessageFactory as _
from izug.poodle.interfaces import IPoodle, IPoodleConfig
from DateTime import DateTime
from Products.statusmessages.interfaces import IStatusMessage

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
        subject = self.context.translate(u"izugpoodle_mail_subject",domain="izugpoodle")
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
    template = ViewPageTemplateFile('poodletable.pt')
    def __call__(self):
        at_tool = getToolByName(self.context,'archetype_tool')
        uid = self.context.REQUEST.get('uid',None)
        if uid:
            context = at_tool.getObject(uid)

        else:
            context = self.context.aq_inner
        return self.template(uid=context.UID())

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
        date = str(date)
        return queryUtility(IURLNormalizer).normalize(user + date)

    def poodleResults(self,data=False):
        
        context = self.context.aq_inner
        if not data:
            data = context.getPoodleData()
        dates = data['dates']
        ids = data['ids']
        #remove the dates entry from list
        data_date_only = data.values()
        data_date_only.remove(dates)
        data_date_only.remove(ids)
        counted = []

        for base_d in ids:
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
        at_tool = getToolByName(self.context,'archetype_tool')
        uid = self.context.REQUEST.get('uid',None)
        if uid:
            obj = at_tool.getObject(uid)
        else:
            obj = self.context.aq_inner
        
        
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

        poodledata = obj.getPoodleData()
        if userid in poodledata.keys():
            for date in poodledata["ids"]:
                if date in dates:
                    poodledata[userid][date] = True
                else: 
                    poodledata[userid][date] = False
        #self.setPoodleData(poodledata)
        #if IPoodle.providedBy(obj):
        #    IPoodleConfig(obj).setPoodleData(data)
        #XXX - use zope dict
        obj.updatePoodleData()
        # use izug.notification if available
        #XXX refactor me (use sendNotification)
        try:
            from izug.notification.base import utils
            mtool = getToolByName(self.context, "portal_membership") 
            template = getattr(self.context, 'poodle_notification')
            creator = self.context.Creator()
            body = template(self,  username=user.getProperty('fullname'), url=self.context.absolute_url())
            to = mtool.getMemberById(creator).getProperty('email')
            utils.send_notification(to_list=[to], cc_list=[], object=object, message=body) 
            
        except ImportError:
            #use old notifyer
            izug_poodle_view.sendNotification(user)
        
        #create journal entry
        journal_view = queryMultiAdapter((self.context, self.context.REQUEST), name="journal_action")
        if journal_view is None:
            return 1
        comment = 'Der Benutzer %s hat an der Umfrage (%s) teilgenommen' % (user.getProperty('fullname'),self.context.Title())
        journal_view.addJournalEntry(obj,comment)

        msg = _(u"Sie haben an der Umfrage teilgenommen.")
        #IStatusMessage(self.request).addStatusMessage(msg, type='info')
        
        return msg
        
class ConvertToMeeting(BrowserView):
    def __call__(self):
        at_tool = getToolByName(self.context,'archetype_tool')
        req = self.context.REQUEST
        uid = req.get('uid',None)
        appendix = req.get('appendix','button_0')
        appendix = appendix.replace('button_','')
        if uid:
            poodle = at_tool.getObject(uid)
        else:
            poodle = self.context.aq_inner

        obj = self.context
        
        #set date inforamtion
        start_date = None
        end_date = None
        time = req.get('date_time_%s' % appendix,None).replace('adm_','').split('-')
        msg_time = self.context.translate(u'poodle_msg_time_failed',domain="izugpoodle")
        msg_date = self.context.translate(u'poodle_msg_date_failed',domain="izugpoodle")
        
        
        if len(time)==2:
            try:
                start_time, end_time = time
                DateTime(start_time)
                DateTime(end_time)
            except:
                #we cannot parse the given time, so make a reset
                start_time, end_time = ['00:00','00:00']
                IStatusMessage(req).addStatusMessage(msg_time, type='error')
        else:
            start_time, end_time = ['00:00','00:00']
            IStatusMessage(req).addStatusMessage(msg_time, type='error')
        
        try:
            date_from = req.get('date_from_%s' % appendix,None).replace('adm_','')
            start_date = DateTime('%s %s' % (date_from,start_time.strip()))
            end_date = DateTime('%s %s' % (date_from,end_time.strip()))
            obj.setStart_date(start_date)
            obj.setEnd_date(end_date)
        except:
            start_date = DateTime()
            end_date = DateTime()
            IStatusMessage(req).addStatusMessage(msg_date, type='error')

        #set date/time
        obj.setStart_date(start_date)
        obj.setEnd_date(end_date)



        users = poodle.getUsers()
        newattendees = []
        for u in users:
            newattendees.append(dict(
                                    contact=u,
                                    ))
                                    
        obj.setAttendees(tuple(newattendees))

        #set type to meeting
        obj.setMeeting_type('meeting_dates_additional')
        obj.processForm()
        
        return 'done'

