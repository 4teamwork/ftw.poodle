from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from ftw.notification.base.interfaces import INotifier
from ftw.poodle import poodleMessageFactory as _
from ftw.poodle.interfaces import IPoodleFilledOutMarker
from ftw.poodle.interfaces import IPoodleVotes
from zope.component import queryMultiAdapter, queryUtility
from zope.interface import directlyProvides, noLongerProvides


class JQSubmitData(BrowserView):
    """Stores the new poodledate and returns a state-message
    """
    def __call__(self):

        self.poodle = self._get_poodle()

        mtool = getToolByName(self.context, "portal_membership")
        member = mtool.getAuthenticatedMember()

        form = self.context.REQUEST.form

        # no dates available
        if not form.values() or form.values() == ['']:
            return False

        self._save_votes(member.id, form.values())
        self._send_notification()
        self._create_journal_entry(member)
        return _(u"You taked part to the poll")

    def _get_poodle(self):
        rc = getToolByName(self.context, 'reference_catalog')
        uid = self.context.REQUEST.get('uid', None)

        if uid:
            return rc.lookupObject(uid)
        else:
            return self.context.aq_inner

    def _save_votes(self, userid, dates):

        votes = IPoodleVotes(self.poodle)
        poodledata = votes.getPoodleData()
        if userid in poodledata['users'].keys():
            for date in poodledata["ids"]:
                poodledata['users'][userid][date] = bool(date in dates)

        votes.setPoodleData(poodledata)

    def _create_journal_entry(self, member):
        """Creates a journal entry - if the journal is available"""
        journal_view = queryMultiAdapter(
            (self.context, self.context.REQUEST), name="journal_action")
        if journal_view:
            comment = _(
                "label_user_has_participated",
                default='The user {fullname} participated in the poll {title}',
                mapping={
                    'fullname': member.getProperty('fullname') or member.id,
                    'title': self.poodle.Title()})

            journal_view.addJournalEntry(self.poodle, comment)

    def _send_notification(self):
        """Sends a notification to the poodle creator,
        with the help of ftw.notification.email"""

        # notify with ftw.notifaction.email
        notifier = queryUtility(INotifier, name='email-notifier')
        directlyProvides(self.context, IPoodleFilledOutMarker)
        notifier.send_notification(
            to_list=[self.context.Creator()],
            object_=self.context)
        noLongerProvides(self.context, IPoodleFilledOutMarker)
