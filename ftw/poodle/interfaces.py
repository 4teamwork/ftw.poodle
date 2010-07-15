from zope.interface import Interface

class IPoodle(Interface):
    """ A 'doodle'-like content type that helps finding a date for a meeting """

class IPoodleVotes(Interface):
    """ Adapter for annotation storage of poodledata """