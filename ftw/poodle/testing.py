from plone.testing import Layer
from plone.testing import zca
from zope.configuration import xmlconfig


class PoodleVotesZCMLLayer(Layer):

    defaultBases = (zca.ZCML_DIRECTIVES, )

    def testSetUp(self):
        self['configurationContext'] = context = \
            zca.stackConfigurationContext(self.get('configurationContext'))

        import zope.annotation
        xmlconfig.file(
            'configure.zcml', zope.annotation, context=context)

        import ftw.poodle
        xmlconfig.file(
            'tests.zcml', ftw.poodle, context=context)

    def testTearDown(self):
        del self['configurationContext']

POODLE_VOTES_ZCML_LAYER = PoodleVotesZCMLLayer()
