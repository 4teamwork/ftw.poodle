from ftw.poodle.interfaces import IPoodle, IPoodleVotes
from ftw.poodle.testing import POODLE_VOTES_ZCML_LAYER
from ftw.testing import MockTestCase
from persistent.mapping import PersistentMapping
from zope.annotation.interfaces import IAttributeAnnotatable


class TestPoodleVotes(MockTestCase):

    layer = POODLE_VOTES_ZCML_LAYER

    def test_getter_setter(self):
        poodle = self.providing_stub(
            [IAttributeAnnotatable, IPoodle])

        self.replay()

        votes = IPoodleVotes(poodle)

        data = votes.getPoodleData()
        self.assertEquals(data, {})

        # we don't have direct wright access
        data['results'] = ['1', '0', '3']
        self.assertTrue(data != votes.getPoodleData())

        votes.setPoodleData(data)
        self.assertEquals(votes.getPoodleData(), data)

        votes.setPoodleData(None)
        self.assertEquals(votes.getPoodleData(), data)

        self.assertEquals(
            type(votes.annotations.get('poodledata')), PersistentMapping)

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

        # second update
        votes.updateDates()

        self.assertEquals(
            votes.getPoodleData().get('dates'),
            ['01.11.2012', '13.11.2012', '20.11.2012'])
        self.assertEquals(votes.getPoodleData().get('ids'), hashes_2)

    def test_update_users(self):

        poodle = self.providing_stub(
            [IAttributeAnnotatable, IPoodle])

        data = {
            'dates': ['12.11.2012', '15.11.2012', '20.11.2012'],
            'ids': ['8097406929898805012', '-4524804321304724558',
                        '4544035125307673798'],
            'users': {
                'hugo.boss': {
                    '8097406929898805012': False,
                    '-4524804321304724558': None,
                    '4544035125307673798': True,
                    '8410780190390256022': None,},
                'james.bond': {
                    '8097406929898805012': True,
                    '-4524804321304724558': True,
                    '4544035125307673798': True,
                    '8410780190390256022': False,},
                'peter.muster': {
                    '8097406929898805012': False,
                    '-4524804321304724558': False,
                    '4544035125307673798': True,
                    '8410780190390256022': False,},
                }
            }

        self.expect(poodle.getUsers()).result(
        ['hugo.boss', 'peter.muster', 'ms.busy'])

        self.replay()

        votes = IPoodleVotes(poodle)
        votes.setPoodleData(data)

        votes.updateUsers()

        self.assertEquals(
            votes.getPoodleData().get('users').keys(),
            ['hugo.boss', 'ms.busy', 'peter.muster'],
            )

        self.assertEquals(
            votes.getPoodleData().get('users').get('ms.busy'),
            {'8097406929898805012': None, '-4524804321304724558': None,
             '4544035125307673798': None,})

        # TODO: should work also, update mehtods should be refactored
        # self.assertEquals(
        #     votes.getPoodleData().get('users').get('hugo.boss').keys(),
        #     ['8097406929898805012', '-4524804321304724558',
        #      '4544035125307673798'])
