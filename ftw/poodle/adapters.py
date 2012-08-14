from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from ftw.notification.email.templates.base import BaseEmailRepresentation
from ftw.poodle import poodleMessageFactory as _
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.i18n import translate


def get_full_name(context):
    mtool = getToolByName(context, "portal_membership")
    member = mtool.getAuthenticatedMember()
    if member.getProperty('fullname'):
        return member.getProperty('fullname')
    return member.id


class PoodleSubjectCreator(object):
    def __init__(self, context):
        self.context = aq_inner(context)
        self.request = self.context.REQUEST

    def __call__(self, object_):

        subject = translate(
            _(u"ftwpoodle_mail_subject",
              default=u"The User ${username} has filled out your poodle",
              mapping={'username':
                           get_full_name(self.context).decode('utf-8')}),
            context=self.request)

        return subject


class PoodleEmailRepresentation(BaseEmailRepresentation):

    template = ViewPageTemplateFile('poodle_notification.pt')

    def fullname(self):
        return get_full_name(self.context)
