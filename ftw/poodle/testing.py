from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import Layer
from plone.testing import z2
from plone.testing import zca
from zope.configuration import xmlconfig
import ftw.poodle.tests.builders


class PoodleVotesZCMLLayer(Layer):

    defaultBases = (zca.ZCML_DIRECTIVES, )

    def testSetUp(self):
        self['configurationContext'] = context = \
            zca.stackConfigurationContext(self.get('configurationContext'))

        import zope.annotation
        xmlconfig.file(
            'configure.zcml', zope.annotation, context=context)

        import zope.traversing
        xmlconfig.file(
            'configure.zcml', zope.traversing, context=context)

        import ftw.poodle
        xmlconfig.file(
            'tests.zcml', ftw.poodle, context=context)

    def testTearDown(self):
        del self['configurationContext']

POODLE_VOTES_ZCML_LAYER = PoodleVotesZCMLLayer()


class FtwLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="Products.DataGridField" />'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'ftw.poodle')
        z2.installProduct(app, 'DataGridField')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.poodle:default')


FTW_FIXTURE = FtwLayer()
FTW_FUNCTIONAL = FunctionalTesting(
    bases=(FTW_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.poodle:functional")
