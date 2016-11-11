from ftw.builder import Builder
from ftw.builder import create
from ftw.poodle.testing import FTW_FUNCTIONAL
from ftw.testbrowser import browsing
from plone.api import user
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from unittest2 import TestCase
import transaction


# Stealth voting is active for all those tests.
class TestStealthVoting(TestCase):

    layer = FTW_FUNCTIONAL

    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)

        self.jane = user.create(email='jane@plone.org',
                                username='jane',
                                password='pw4jane')
        self.jack = user.create(email='jack@plone.org',
                                username='jack',
                                password='pw4jack')

        self.folder = create(Builder('folder').titled('Workspaces'))

        dates = [
            {'date': '01.11.2016', 'duration': '15:00-16:00'},
            {'date': '15.11.2016', 'duration': '12:00-18:00'},
            {'date': '20.11.2016', 'duration': '13.00-14.00'}]

        users = [self.jane.getId(), self.jack.getId()]

        self.poodle = create(Builder('poodle').titled('poodle')
                                              .within(self.folder)
                                              .having(dates=dates,
                                                      users=users,
                                                      stealth_voting=True))

        transaction.commit()

    @browsing
    def test_user_can_only_see_his_own_voting(self, browser):
        browser.login('jane', 'pw4jane').visit(self.poodle)

        self.assertEqual(1, len(browser.css('table.poodletable tr.poodle-user')))
        self.assertEqual(self.jane.getName(),
                         browser.css('table.poodletable tr.poodle-user td.user').first.text)

    @browsing
    def test_owner_can_see_every_voting(self, browser):
        browser.login().visit(self.poodle)

        self.assertEqual(2, len(browser.css('table.poodletable tr.poodle-user')))

    @browsing
    def test_only_owner_can_see_results(self, browser):
        browser.login('jane', 'pw4jane').visit(self.poodle)

        self.assertFalse(browser.css('table.poodletable tr.poodle-results'))

        browser.login().visit(self.poodle)

        self.assertEqual(1, len(browser.css('table.poodletable tr.poodle-results')))
