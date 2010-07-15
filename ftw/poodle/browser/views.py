from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName  
from zope.component import getMultiAdapter, queryMultiAdapter 
from ftw.poodle import poodleMessageFactory as _


class JQSubmitData(BrowserView):
    def __call__(self):
        ftw_poodle_view = getMultiAdapter((self.context, self.request), name=u'ftw_poodle_view')
        rc = getToolByName(self.context,'reference_catalog')
        uid = self.context.REQUEST.get('uid',None)
        if uid:
            obj = rc.lookupObject(uid)
        else:
            obj = self.context.aq_inner
        
        
        #woke up archetype 10times
        #ftw_poodle_view.saveData()
        
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
        
        ftw_poodle_view.sendNotification(user)
        
        #create journal entry
        journal_view = queryMultiAdapter((self.context, self.context.REQUEST), name="journal_action")
        if journal_view is None:
            return 1
        comment = 'Der Benutzer %s hat an der Umfrage (%s) teilgenommen' % (user.getProperty('fullname'),self.context.Title())
        journal_view.addJournalEntry(obj,comment)

        msg = _(u"Sie haben an der Umfrage teilgenommen.")
        #IStatusMessage(self.request).addStatusMessage(msg, type='info')
        
        return msg
        
