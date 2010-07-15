from Products.Five.browser import BrowserView 
from Products.CMFCore.utils import getToolByName  
from zope.component import getMultiAdapter 
from zope.component import queryUtility
from plone.i18n.normalizer.interfaces import IURLNormalizer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class PoodleTableView(BrowserView):
    
    template = ViewPageTemplateFile('templates/poodletable.pt')
    
    def __call__(self):
        rc = getToolByName(self.context,'reference_catalog')
        uid = self.context.REQUEST.get('uid',None)
        if uid:
            context = rc.lookupObject(uid)

        else:
            context = self.context.aq_inner
        return self.template(uid=context.UID())

    def isCurrentUser(self, userid):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        user = portal_state.member()
        return user.id == userid

    def getUserFullname(self, userid):
        mtool = getToolByName(self.context, "portal_membership") 
        return mtool.getMemberById(userid).getProperty('fullname')

    def getCssClass(self, data):
        if data == None: return "not_voted"
        elif data == True: return "positive"
        elif data == False: return "negative"

    def getInputId(self, user, date):
        date = str(date)
        return queryUtility(IURLNormalizer).normalize(user + date)

    def poodleResults(self,data=False):
        
        context = self.context.aq_inner
        if not data:
            data = context.getPoodleData()
        ids = data['ids']
        users = data['users'].values()
        counted = []

        for base_d in ids:
            counter = 0
            for d in users:
                if d[base_d]:
                    counter += 1
            counted.append(counter)
                    
        #get highest value
        heightest = counted[:]
        heightest.sort()
        heightest.reverse()
        h_value = heightest[:1] and heightest[:1][0] or 0
        html_data = ''
        for v in counted:
            if v == h_value:
                v = "<b>%s</b>" % v
            html_data += "<td>%s</td>" % v
        return html_data