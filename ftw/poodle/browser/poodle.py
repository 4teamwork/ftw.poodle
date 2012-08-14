from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from ftw.poodle import poodleMessageFactory as _
from zope.component import getMultiAdapter


class PoodleView(BrowserView):
    """ View of a poodle object
    """
    template = ViewPageTemplateFile('templates/poodle.pt')

    def __call__(self):
        if not self.check_mail_settings():
            msg = """Wrong email-settings, please check control panel.
            At time it's not possible to send email notification about
            attendees, who vote. """
            IStatusMessage(self.request).addStatusMessage(
                msg,
                type='warning')

        if not self.is_active():
            msg = _(u"survey_deactivated", default=u"Survey is deactivated")
            IStatusMessage(self.request).addStatusMessage(
                msg,
                type='info')

        return self.template()

    def check_mail_settings(self):
        """check for correct mail settings - use control panel"""
        portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state')
        portal = portal_state.portal()
        ctrlOverview = getMultiAdapter((portal, portal.REQUEST),
                                        name='overview-controlpanel')
        mail_settings_correct = not ctrlOverview.mailhost_warning()

        if mail_settings_correct:
            return True
        return False

    def renderTable(self, context):
        """render the poodle table
        """
        view = context.restrictedTraverse('@@ftw_poodle_table')
        return view()

    def is_active(self):
        """Checks the portal state if poodle is active
        TODO: Add a real security guard
        TOFO: defined twice - copied from poodletable
        """
        context_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_context_state')
        obj_state = context_state.workflow_state()

        return obj_state == 'open'
