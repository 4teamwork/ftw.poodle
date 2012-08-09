from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations
from interfaces import IPoodle, IPoodleVotes
from persistent.mapping import PersistentMapping


class PoodleVotes(object):
    implements(IPoodleVotes)
    adapts(IPoodle)

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)

    def getPoodleData(self):
        """getter for poodledata
        """
        if self.annotations.get('poodledata'):
            return self.annotations.get('poodledata').data
        return {}

    def setPoodleData(self, data):
        """setter for poodledata
        """
        if data:
            self.annotations['poodledata'] = PersistentMapping(data)

    def updateDates(self):
        """updates date informations
        """
        poodledata = self.getPoodleData()

        dates = self.context.getDates()
        poodledata["dates"] = [i['date'] for i in dates]
        poodledata['ids'] = self.context.getDatesHash()

        self.setPoodleData(poodledata)

    def updateUsers(self):
        """uddate user informations
        """

        poodledata = self.getPoodleData()
        users = self.context.getUsers()
        # create ids part if not available
        if 'ids' not in poodledata:
            poodledata['ids'] = {}
        choices = poodledata['ids']
        # create a users part if not available
        if 'users' not in poodledata:
            poodledata['users'] = {}

        for user in users:
            if user not in poodledata['users'].keys():
                # add user to data and fill dates with None
                userdates = {}
                [userdates.setdefault(choice) for choice in choices]
                poodledata['users'][user] = userdates
            else:
                # check if the dates are correct
                userdates = poodledata['users'][user]
                for choice in choices:
                    if choice not in userdates.keys():
                        # a new date
                        userdates[choice] = None

        # check if we need to remove any users from poodledata
        for user in poodledata['users'].keys():
            if user not in users:
                del(poodledata['users'][user])

        self.setPoodleData(poodledata)
