from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.component import queryUtility
from plone.i18n.normalizer.interfaces import IURLNormalizer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PoodleTableView(BrowserView):
    """Renders the poodle table
    The table is seperated from the poodleview, so we can reload
    the table per ajax.
    """

    template = ViewPageTemplateFile('templates/poodletable.pt')
    voted_template = ViewPageTemplateFile('templates/voted.pt')

    def __call__(self):
        """
        """
        rc = getToolByName(self.context, 'reference_catalog')
        uid = self.request.get('uid', None)
        voted = self.request.get('voted', None)
        if uid:
            context = rc.lookupObject(uid)

        else:
            context = self.context.aq_inner
        if voted:
            return self.voted_template()
        return self.template(uid=context.UID())

    def isCurrentUser(self, userid):
        """returns bool value if the given user
        is the current loggedin user

        """
        portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state')
        user = portal_state.member()
        # also add is poodle active check
        return user.id == userid and self.is_active()

    def getUserFullname(self, userid):
        """returns fullname of a given user
        """
        mtool = getToolByName(self.context, "portal_membership")
        member = mtool.getMemberById(userid)
        if not member:
            return userid
        fullname = member.getProperty('fullname')
        if not fullname:
            return userid
        return fullname

    def getCssClass(self, data):
        """returns three diffrent css class-names
        depending on the data param.

        """
        if data is None:
            return "not_voted"
        elif data is True:
            return "positive"
        elif data is False:
            return "negative"

    def getInputId(self, user, date):
        """generates the unique and normalized id for the checkboxes"""

        date = str(date)
        return queryUtility(IURLNormalizer).normalize(user + date)

    def poodleResults(self, data=None, print_html=True):
        """count all user votes per date
        will be displayed at the bottom of the table

        This method is traversable (allowed_attributes)

        """
        context = self.context.aq_inner
        if not data:
            data = context.getPoodleData()
        ids = data['ids']
        users = data['users'].values()
        result = []

        for base_d in ids:
            counter = 0
            for d in users:
                if d[base_d]:
                    counter += 1
            result.append(counter)

        # if result is still empty return empty string
        if not result:
            return ""

        # TODO: store the calculation in poodle_votes adapter
        if not print_html:
            data['result'] = result
            return data
        h_value = max(result)

        # render a small part html for the last table row
        html_data = ''
        for v in result:
            if v == h_value:
                v = "<b>%s</b>" % v
            html_data += "<td>%s</td>" % v
        return html_data

    def show_inputs(self):
        """returns bool value if user can vote"""

        portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state')
        user = portal_state.member()

        # added is_active check, to find out if poodle is active or not
        return (user.id in self.context.getUsers()) and self.is_active()

    def is_active(self):
        """Checks the portal state if poodle is active
        TODO: Add a real security guard

        """
        context_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_context_state')
        obj_state = context_state.workflow_state()

        return obj_state == 'open'
