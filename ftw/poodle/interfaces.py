from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager


class IPoodle(Interface):
    """A 'doodle'-like content type that 
    helps finding a date for a meeting

    """

class IPoodleVotes(Interface):
    """Adapter for annotation storage of poodledata """
    
class IPoodletableBottom(IViewletManager):
    """Free slot to display other informations or integration of other
    packages. 

    """