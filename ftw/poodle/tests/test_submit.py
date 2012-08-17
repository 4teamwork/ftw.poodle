from ftw.notification.base.interfaces import INotifier
from ftw.poodle.browser.submit_data import JQSubmitData
from ftw.poodle.interfaces import IPoodle, IPoodleVotes
from ftw.poodle.testing import POODLE_VOTES_ZCML_LAYER
from ftw.testing import MockTestCase
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import Interface


SAMPLE_DATA = {
    'dates': ['12.11.2012', '15.11.2012', '20.11.2012'],
    'ids': ['3780942686938285155', '-4524804321304724558',
                '-5507833967094327526', '4544035125307673798'],
    'users': {
        'hugo.boss': {
            '3780942686938285155': False,
            '-4524804321304724558': None,
            '4544035125307673798': True,
            '-5507833967094327526': None, },
        'james.bond': {
            '3780942686938285155': True,
            '-4524804321304724558': True,
            '4544035125307673798': True,
            '-5507833967094327526': False, },
        }
    }


class TestJQSubmit(MockTestCase):

    layer = POODLE_VOTES_ZCML_LAYER

    def test_get_poodle(self):
        poodle = self.stub()
        request = self.stub()
        self.expect(poodle.REQUEST).result(request)
        self.expect(poodle.aq_inner).result(poodle)

        rc = self.stub()
        self.mock_tool(rc, 'reference_catalog')
        self.expect(rc.lookupObject('FAKE_UID')).result('FAKE_OBJ')

        with self.mocker.order():
            self.expect(request.get('uid', None)).result('FAKE_UID')

            self.expect(request.get('uid', None)).result(None)

        self.replay()

        # 1
        self.assertEquals(
            JQSubmitData(poodle, request)._get_poodle(), 'FAKE_OBJ')
        # 2
        self.assertEquals(
            JQSubmitData(poodle, request)._get_poodle(), poodle)

    def test_save_votes(self):

        poodle = self.providing_stub([IAttributeAnnotatable, IPoodle])
        request = self.stub()

        self.replay()

        data = IPoodleVotes(poodle).setPoodleData(SAMPLE_DATA)

        submit_view = JQSubmitData(poodle, request)
        submit_view.poodle = poodle
        submit_view._save_votes(
            'hugo.boss', ['3780942686938285155', '-5507833967094327526'])
        submit_view._save_votes(
            'james.bond', [])

        data = IPoodleVotes(poodle).getPoodleData()
        # check hugo boss his new votes
        self.assertEquals(
            data.get('users').get('hugo.boss'),
            {'3780942686938285155': True, '-4524804321304724558': False,
             '4544035125307673798': False, '-5507833967094327526': True, })

        # check bonds new votes
        self.assertEquals(
            data.get('users').get('james.bond'),
            {'3780942686938285155': False, '-4524804321304724558': False,
             '4544035125307673798': False, '-5507833967094327526': False, })

    def test_create_journal_entry(self):

        poodle = self.stub()
        request = self.stub()
        self.expect(poodle.REQUEST).result(request)
        self.expect(poodle.Title()).result('Test Poll')

        user = self.stub()
        self.expect(user.getProperty('fullname')).result('Hugo Boss')

        journal_view = self.stub()
        self.mock_adapter(
            journal_view, Interface, [Interface, Interface], name='journal_action')

        self.expect(journal_view(poodle, request)).result(journal_view)
        self.expect(journal_view.addJournalEntry(
                poodle, u'label_user_has_participated'))
        self.replay()

        view = JQSubmitData(poodle, request)
        view.poodle = poodle
        view._create_journal_entry(user)

    def test_notification(self):
        request = self.stub()
        poodle = self.create_dummy(
            REQUEST=request,
            Title='Test Poll',
            Creator=lambda: 'hugo.boss')

        notifier = self.stub()
        self.mock_utility(
            notifier, INotifier, name='email-notifier')
        self.expect(
            notifier.send_notification(to_list=['hugo.boss'], object_=poodle))

        self.replay()

        view = JQSubmitData(poodle, request)
        view.poodle = poodle

        view._send_notification()
