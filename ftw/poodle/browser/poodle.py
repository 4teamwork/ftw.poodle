from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName  
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile



class PoodleView(BrowserView):
    """ View of a poodle object
    """
    template = ViewPageTemplateFile('templates/poodle.pt')
    
    def __call__(self):
        return self.template()
        

    def getUserFullname(self, userid):
        """returns the fullname of a given user
        """
        mtool = getToolByName(self.context, "portal_membership") 
        return mtool.getMemberById(userid).getProperty('fullname')

            
        
    def sendNotification(self, user):
        """Sends a notification after someone filled out the meeting poll
        """
        mtool = getToolByName(self.context, "portal_membership") 
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        site_properties = getToolByName(self.context, 'portal_properties').site_properties
        
        host = getToolByName(self.context, "MailHost")
        creator = self.context.Creator() # send a mail to the creator of the poll
        send_to_address = mtool.getMemberById(creator).getProperty('email')
        if send_to_address == '': send_to_address = site_properties.email_from_address
        send_from_address = site_properties.email_from_address
        subject = self.context.translate(u"ftwpoodle_mail_subject",domain="ftw.poodle")
        template = getattr(self.context, 'poodle_notification')
        encoding = portal.getProperty('email_charset')
        # Cook from template
        message = template(self,  username=self.getUserFullname(user.id), url=self.context.absolute_url())
        host.send(messageText = message, 
                  mto = send_to_address,
                  mfrom = send_from_address, 
                  subject = subject, 
                  charset = encoding,
                  )

            #{'form.button.Save': 'Speichern', 'hamu2.12.2008': '2.12.2008', 'hamu13.7.82': '13.7.82'}
        
        

    def renderTable(self, context):
        """render the poodle table
        """
        view = context.restrictedTraverse('@@ftw_poodle_table')
        return view()