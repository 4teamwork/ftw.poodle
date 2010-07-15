from Products.CMFCore.utils import getToolByName

def fix_poodles(portal_setup):
    catalog = getToolByName(portal_setup, 'portal_catalog')
    results = [x.getObject() for x in catalog(Type='Meeting')]
    for result in results:
        if result.getMeeting_type() == 'poodle_additional':
            pd = result.getPoodleData()
            if not pd.has_key('ids'):
               pd['ids'] = result.getAviableChoices()
               dates = dict([(a['date'],str(hash('%s%s' % (a['date'],a['duration'])))) for a in result.getDates()])
               for user,values in pd.items():
                   if not isinstance(values, dict):
                       continue
                   for date, value in values.items():
                       hash_ = dates.get(date)
                       if hash_:
                           values[hash_] = value
               result.setPoodleData(pd)
            result.reindexObject()

    return 'migration done'
