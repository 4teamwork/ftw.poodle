from Products.Five.browser import BrowserView

from AccessControl import getSecurityManager  
from Products.CMFCore.utils import getToolByName  
from zope.component import getMultiAdapter  
from zope.component import queryUtility

from plone.i18n.normalizer.interfaces import IURLNormalizer


from izug.poodle.interfaces import IPoodle, IPoodleConfig


class PoodleView(BrowserView):
    
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
        date = date['date']
        return queryUtility(IURLNormalizer).normalize(user + date)
    
    def saveData(self):
        if hasattr(self.context.REQUEST, 'form'):
            portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
            user = portal_state.member()
            form = self.context.REQUEST.form
            self.context.saveUserData(user.id, form.values())
            #{'form.button.Save': 'Speichern', 'hamu2.12.2008': '2.12.2008', 'hamu13.7.82': '13.7.82'}
        
        
        