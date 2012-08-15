from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations
from interfaces import IPoodle, IPoodleVotes
from persistent.mapping import PersistentMapping
from persistent.list import PersistentList


def make_persistent(data):
    if isinstance(data, dict) or \
            isinstance(data, PersistentMapping):

        data = PersistentMapping(data)

        for key, value in data.items():
            value = make_persistent(value)
            data[key] = value

    elif isinstance(data, list) or \
            isinstance(data, PersistentList):

        new_data = PersistentList()
        for item in data:
            new_data.append(make_persistent(item))
        data = new_data

    return data


class PoodleVotes(object):
    implements(IPoodleVotes)
    adapts(IPoodle)

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)

    def getPoodleData(self):
        """getter for poodledata
        """
        if not self.annotations.get('poodledata'):
            self.annotations['poodledata'] = PersistentMapping()
        return self.annotations['poodledata']

    def setPoodleData(self, data):
        """setter for poodledata
        """
        if data:
            self.annotations['poodledata'] = PersistentMapping(
                make_persistent(data))

    def updateDates(self):
        """updates date informations
        """
        poodledata = self.getPoodleData()

        dates = self.context.getDates()
        poodledata["dates"] = [i['date'] for i in dates]
        poodledata['ids'] = self.context.getDatesHash()

        # clean up the old dates in the users votes
        for user in poodledata.get('users', {}).keys():
            for date_hash in poodledata.get('users').get(user).keys():
                if date_hash not in poodledata.get('ids'):
                    poodledata.get('users').get(user).pop(date_hash)

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
