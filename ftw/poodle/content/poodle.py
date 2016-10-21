from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column
from ftw.poodle import poodleMessageFactory as _
from ftw.poodle.config import PROJECTNAME
from ftw.poodle.interfaces import IPoodle, IPoodleVotes
from zope.interface import implements


PoodleSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

        atapi.LinesField(
            name='users',
            vocabulary_factory="ftw.poodle.users",
            enforceVocabulary=True,
            widget=atapi.InAndOutWidget(
                label=_(u'ftwpoodle_label_users', default=u'Users'),
                actb_expand_onfocus=1),
            required=1,
            multiValued=1),

        DataGridField(
            name='dates',
            allow_empty_rows=False,
            widget=DataGridWidget(
                columns={
                    "date": Column(_(u"ftwpoodle_desc_date",
                                     default="Date"),
                                   col_description=_("ftwpoodle_help_date",
                                                     default="Provide a date in a format like MM-DD-AAAA"),
                                   required=True),
                    "duration": Column(_(u"ftwpoodle_desc_duration",
                                         default="Time / Duration"),
                                       required=True),
                    },
                label=_(u'ftwpoodle_label_dates', default=u'Dates')),
            columns=("date", "duration")),

        atapi.BooleanField(
            name="stealth_voting",
            widget=atapi.BooleanWidget(
                label=_(u'stealth_voting', default=u'Enable stealth voting'),
            ),
            default=True,
            required=False
        ),

        ))


schemata.finalizeATCTSchema(PoodleSchema, moveDiscussion=False)


class Poodle(base.ATCTContent):
    """ A 'doodle'-like content type that helps finding a date for a meeting
    """

    implements(IPoodle)

    security = ClassSecurityInfo()

    portal_type = "Meeting poll"
    schema = PoodleSchema

    security.declarePrivate("getDatesHash")

    def getDatesHash(self):
        return [str(hash('%s%s' % (a['date'], a['duration'])))
                for a in self.getDates()]

    security.declarePrivate("getPoodleData")

    def getPoodleData(self):
        if IPoodle.providedBy(self):
            return IPoodleVotes(self).getPoodleData()
        return {}

    def get_poodle_votes(self):
        if IPoodle.providedBy(self):
            return IPoodleVotes(self)

    security.declarePrivate("setPoodleData")

    def setPoodleData(self, data):
        if IPoodle.providedBy(self):
            IPoodleVotes(self).setPoodleData(data)

    security.declarePrivate("updatePoodleData")

    def updatePoodleData(self):
        votes = self.get_poodle_votes()
        votes.updateDates()
        votes.updateUsers()
        self.updateSharing()

    security.declarePrivate("updateSharing")

    def updateSharing(self):
        """
        Allow the selected Users to view the object
        """
        users = self.getUsers()
        for user in users:
            wanted_roles = [u'Reader']
            wanted_roles += list(self.get_local_roles_for_userid(user))
            self.manage_setLocalRoles(user, wanted_roles)
        self.reindexObjectSecurity()
        # XXX: remove users?

    security.declarePrivate("saveUserData")

    def saveUserData(self, userid, dates):
        votes = self.get_poodle_votes()
        poodledata = votes.getPoodleData()
        if userid in poodledata['users'].keys():
            for date in poodledata["dates"]:
                poodledata['users'][userid][date] = bool(date in dates)
        votes.setPoodleData(poodledata)

    def getMeeting_type(self):
        """Set meeting type for tabbed-view compatibility in ftw.workspace.
        """
        return 'poll'


atapi.registerType(Poodle, PROJECTNAME)
