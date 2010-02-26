from Products.CMFCore.utils import getToolByName

def fix_poodles(portal_setup):
    catalog = getToolByName(portal_setup, 'portal_catalog')
    results = [x.getObject() for x in catalog(Type='Meeting')]
    for result in results:
        if result.getMeeting_type() == 'poodle_additional':
            result.updatePoodleData()
            result.reindexObject()

    return 'migration done'