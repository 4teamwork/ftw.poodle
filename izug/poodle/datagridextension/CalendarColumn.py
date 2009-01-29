from __future__ import nested_scopes

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.DataGridField.Column import Column

class CalendarColumn(Column):
    """ Column with calendar widget
    """
    security = ClassSecurityInfo()
        
    security.declarePublic('getMacro')
    def getMacro(self):
        """ Return macro used to render this column in view/edit """
        return "datagrid_calendar_cell"
        
    security.declarePublic('processCellData')
    def processCellData(self, form, value, context, field, columnId):
        """ Read cell values from raw form data
        
        Column processing in forms may need special preparations for data if
        widgets use other than <input value> for storing their
        values in fields.
        
        @param form Submitted form, contains HTML fields
        @param context Archetypes item instance for the submitted form
        @param field Assigned field for this widget
        @param columnId Column what we are operating
        
        @return new values which are constructed by processing data
        """
        newValue = []
        
        for row in value:
            
            # we must clone row since
            # row is readonly ZPublished.HTTPRequest.record object
            newRow = {}
            for key in row.keys():
                newRow[key] = row[key]
                        
            orderIndex = row["orderindex_"] 
            cellId = "%s_%s_%s" % (field.getName(), columnId, orderIndex)
            if form.has_key(cellId):
                # If check button is set in HTML form
                # it's id appears in form of field.column.orderIndex
                # field value is hardcoded to '1'
                newRow[columnId] = form[cellId]
            else:
                # if item is not in form, user did not check it.
                newRow[columnId] = ''
                
            newValue.append(newRow)
            
        return newValue

InitializeClass(CalendarColumn)
