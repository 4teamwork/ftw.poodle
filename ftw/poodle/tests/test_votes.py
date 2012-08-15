from ftw.poodle.interfaces import IPoodle, IPoodleVotes
from ftw.poodle.testing import POODLE_VOTES_ZCML_LAYER
from ftw.testing import MockTestCase
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from zope.annotation.interfaces import IAttributeAnnotatable


SAMPLE_DATA = {
    'dates': ['12.11.2012', '15.11.2012', '20.11.2012'],
    'ids': ['3780942686938285155', '-4524804321304724558',
                '-5507833967094327526'],
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
        'peter.muster': {
            '3780942686938285155': False,
            '-4524804321304724558': False,
            '4544035125307673798': True,
            '-5507833967094327526': False, },
        }
    }


class TestPoodleVotes(MockTestCase):

    layer = POODLE_VOTES_ZCML_LAYER

    def test_getter_setter(self):
        poodle = self.providing_stub(
            [IAttributeAnnotatable, IPoodle])

        self.replay()

        votes = IPoodleVotes(poodle)

        data = votes.getPoodleData()
        self.assertEquals(data, {})

        # we have direct wright access
        data['results'] = ['1', '0', '3']
        self.assertTrue(data == votes.getPoodleData())

        votes.setPoodleData(data)
        self.assertEquals(votes.getPoodleData(), data)

        votes.setPoodleData(None)
        self.assertEquals(votes.getPoodleData(), data)

        self.assertEquals(
            type(votes.annotations.get('poodledata')), PersistentMapping)

    def test_recursive_persistent(self):
        poodle = self.providing_stub(
            [IAttributeAnnotatable, IPoodle])

        self.replay()

        votes = IPoodleVotes(poodle)

        votes.setPoodleData(PersistentMapping(SAMPLE_DATA))
        data = votes.getPoodleData()

        self.assertTrue(type(data.get('dates')) == PersistentList)
        self.assertTrue(type(data.get('ids')) == PersistentList)
        self.assertTrue(type(data.get('users')) == PersistentMapping)
        self.assertTrue(type(data.get('users').get('james.bond')),
                        PersistentMapping)

    def test_update_dates(self):
        poodle = self.providing_stub(
            [IAttributeAnnotatable, IPoodle])

        dates_1 = [
            {'date':'01.11.2012', 'duration':'15:00-16:00'},
            {'date':'15.11.2012', 'duration':'12:00-18:00'},
            {'date':'20.11.2012', 'duration':'13.00-14.00'}]

        hashes_1 = [
            str(hash('%s%s' % (a['date'], a['duration']))) for a in dates_1]

        dates_2 = [
            {'date':'01.11.2012', 'duration':'15:00-16:00'},
            {'date':'13.11.2012', 'duration':'only Text'},
            {'date':'20.11.2012', 'duration':'13.00-14.00'}]

        hashes_2 = [
            str(hash('%s%s' % (a['date'], a['duration']))) for a in dates_2]

        with self.mocker.order():
            self.expect(poodle.getDates()).result(dates_1)
            self.expect(poodle.getDatesHash()).result(hashes_1)

            self.expect(poodle.getDates()).result(dates_2)
            self.expect(poodle.getDatesHash()).result(hashes_2)

        self.replay()

        votes = IPoodleVotes(poodle)

        # first update
        votes.updateDates()

        self.assertEquals(
            votes.getPoodleData().get('dates'),
            ['01.11.2012', '15.11.2012', '20.11.2012'])
        self.assertEquals(votes.getPoodleData().get('ids'), hashes_1)

        votes.setPoodleData(SAMPLE_DATA)

        # second update
        votes.updateDates()

        self.assertEquals(
            votes.getPoodleData().get('dates'),
            ['01.11.2012', '13.11.2012', '20.11.2012'])
        self.assertEquals(votes.getPoodleData().get('ids'), hashes_2)

        for date_hash in votes.getPoodleData().get(
            'users').get('hugo.boss').keys():
            self.assertTrue(date_hash in hashes_2)

    def test_update_users(self):

        poodle = self.providing_stub(
            [IAttributeAnnotatable, IPoodle])

        self.expect(poodle.getUsers()).result(
        ['hugo.boss', 'peter.muster', 'ms.busy'])

        self.replay()

        votes = IPoodleVotes(poodle)
        votes.setPoodleData(SAMPLE_DATA)

        votes.updateUsers()

        users = votes.getPoodleData().get('users')
        self.assertIn('hugo.boss', users)
        self.assertIn('peter.muster', users)
        self.assertIn('ms.busy', users)

        self.assertEquals(
            votes.getPoodleData().get('users').get('ms.busy'),
            {'3780942686938285155': None, '-4524804321304724558': None,
             '-5507833967094327526': None, })
