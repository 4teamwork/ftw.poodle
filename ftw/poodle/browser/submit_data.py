from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter, queryMultiAdapter
from ftw.poodle import poodleMessageFactory as _
from ftw.poodle.interfaces import IPoodleVotes


class JQSubmitData(BrowserView):
    """Stores the new poodledate and returns a state-message
    """
    def __call__(self):
        ftw_poodle_view = getMultiAdapter(
            (self.context, self.request), name=u'ftw_poodle_view')
        rc = getToolByName(self.context, 'reference_catalog')
        uid = self.context.REQUEST.get('uid', None)
        if uid:
            obj = rc.lookupObject(uid)
        else:
            obj = self.context.aq_inner

        portal_state = getMultiAdapter(
            (self.context, self.request), name=u'plone_portal_state')
        user = portal_state.member()
        userid = user.id
        form = self.context.REQUEST.form
        dates = form.values()

        # no dates available
        if dates == ['']:
            return 1

        # change values
        votes = IPoodleVotes(obj)
        poodledata = votes.getPoodleData()
        if userid in poodledata['users'].keys():
            for date in poodledata["ids"]:
                poodledata['users'][userid][date] = bool(date in dates)

        votes.setPoodleData(poodledata)

        # sends email notification to th owner
        ftw_poodle_view.sendNotification(user)

        # status message
        msg = _(u"Sie haben an der Umfrage teilgenommen.")

        #create journal entry - if available
        journal_view = queryMultiAdapter(
            (self.context, self.context.REQUEST), name="journal_action")
        if journal_view is None:
            return msg

        comment = 'Der Benutzer %s hat an der Umfrage (%s) teilgenommen' % (
            user.getProperty('fullname'), self.context.Title())
        journal_view.addJournalEntry(obj, comment)

        return msg
