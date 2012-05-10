from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from Products.statusmessages.interfaces import IStatusMessage
from ftw.poodle import poodleMessageFactory as _

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

    def getUserFullname(self, userid):
        """returns fullname of a given user
        """
        mtool = getToolByName(self.context, "portal_membership")
        fullname = mtool.getMemberById(userid).getProperty('fullname')
        if not fullname:
            return userid
        return fullname

    def sendNotification(self, user):
        """Sends a notification after someone filled out the meeting poll
        """
        mtool = getToolByName(self.context, "portal_membership")
        portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state')
        portal = portal_state.portal()
        site_properties = getToolByName(
            self.context,
            'portal_properties').site_properties

        host = getToolByName(self.context, "MailHost")
        # send a mail to the creator of the poll
        creator = self.context.Creator()
        send_to_address = mtool.getMemberById(creator).getProperty('email')
        if send_to_address == '':
            send_to_address = site_properties.email_from_address
        send_from_address = site_properties.email_from_address
        username = self.getUserFullname(user.id)
        subject = self.context.translate(_(u"ftwpoodle_mail_subject", default=u"The User ${username} has filled out your poodle", mapping={'username':username}))

        template = getattr(self.context, 'poodle_notification')
        encoding = portal.getProperty('email_charset')
        # Cook from template
        message = template(
            self,
            username=username,
            url=self.context.absolute_url())

        # in case of wrong mail_settings, the creator will be informed after
        # creation
        if self.check_mail_settings():
            host.send(messageText = message,
                      mto = send_to_address,
                      mfrom = send_from_address,
                      subject = subject,
                      charset = encoding,
                      )

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