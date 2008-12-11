from Products.Five.browser import BrowserView

from AccessControl import getSecurityManager  
from Products.CMFCore.utils import getToolByName  
from zope.component import getMultiAdapter  


class PoodleView(BrowserView):
    def getTableData(self):
        users = self.context.getUsers()
        dates = self.context.getDates()
        #for user in users:
        #    for date in dates: 

    def getCurrentUser(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        user = portal_state.member()
        return user
    
    def getUserFullname(self, userid):
        mtool = getToolByName(self, "portal_membership") 
        return mtool.getMemberById(userid).getProperty('fullname')
