from Products.Archetypes.interfaces.base import IBaseObject
from Products.CMFCore.interfaces._content import IContentish
from ftw.notification.email.adapters import BaseSubjectCreator
from ftw.notification.email.interfaces import IEMailRepresentation
from ftw.notification.email.interfaces import ISubjectCreator
from ftw.notification.email.templates.base import BaseEmailRepresentation
from ftw.poodle.interfaces import IPoodleFilledOutMarker, IPoodle
from ftw.poodle.testing import POODLE_VOTES_ZCML_LAYER
from ftw.testing import MockTestCase
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView


class TestNotificationAdapters(MockTestCase):

    layer = POODLE_VOTES_ZCML_LAYER

    def test_filled_out_subject_creator(self):
        poodle = self.providing_stub([IPoodleFilledOutMarker])
        request = self.stub_request()
        self.expect(poodle.REQUEST).result(request)

        mtool = self.stub()
        member = self.stub()
        self.mock_tool = self.mock_tool(mtool, 'portal_membership')
        self.expect(mtool.getAuthenticatedMember()).result(member)
        self.expect(member.getProperty('fullname')).result('Hugo Boss')

        self.replay()

        subject = ISubjectCreator(poodle)(poodle)
        self.assertEquals(
            subject, u'The User Hugo Boss has filled out your poodle')

    def test_filled_out_email_representation(self):
        # poodle and request stuff
        poodle = self.providing_stub([IPoodleFilledOutMarker])
        request = self.stub_request()
        self.expect(poodle.REQUEST).result(request)
        self.expect(poodle.absolute_url).result(
            'http://localhost:8080/platform/poodle-1')

        # portal state mocks
        portal_state = self.stub()
        self.mock_adapter(portal_state, IBrowserView,
            [Interface, Interface], name='plone_portal_state')
        self.expect(portal_state(poodle, request)).result(portal_state)
        portal = self.stub()
        self.expect(portal_state.portal_url).result(
            'http://localhost:8080/platform')
        self.expect(portal_state.portal).result(portal)
        self.expect(portal.__call__()).result(portal)
        self.expect(portal()).result(portal)
        self.expect(portal.Title()).result('My poodle portal')

        # member tool mocks
        mtool = self.stub()
        member = self.stub()
        self.mock_tool(mtool, 'portal_membership')
        self.expect(mtool.getAuthenticatedMember()).result(member)
        self.expect(member.getProperty('fullname')).result(None)
        self.expect(member.id).result('hugo.boss')

        self.replay()

        email = IEMailRepresentation(poodle)

        self.assertEquals(
            email.template(),'\n\n The user hugo.boss\n has entered his data into the meeting poll at\n http://localhost:8080/platform/poodle-1\n on the website My poodle portal\n at http://localhost:8080/platform\n\n\n')

    def test_regular_notications(self):
        poodle = self.providing_stub(
            [IPoodle, IContentish, IBaseObject])

        request = self.stub_request()
        self.expect(poodle.REQUEST).result(request)

        self.replay()


        self.assertEquals(
            type(IEMailRepresentation(poodle)),
            BaseEmailRepresentation)

        self.assertEquals(
            type(ISubjectCreator(poodle)),
            BaseSubjectCreator)
