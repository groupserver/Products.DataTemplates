#@PydevCodeAnalysisIgnore
##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
""" Customizable properties that come from the filesystem.

$Id: FSPropertiesObject.py,v 1.2 2003/10/24 12:25:21 philikon Exp $
"""

import Globals
import Acquisition
from OFS.Folder import Folder
from OFS.PropertyManager import PropertyManager
from ZPublisher.Converters import get_converter
from AccessControl import ClassSecurityInfo

from Products.FileSystemSite.utils import _dtmldir
from Products.FileSystemSite.DirectoryView import registerFileExtension, registerMetaType, expandpath
from Products.FileSystemSite.Permissions import ViewManagementScreens
from Products.FileSystemSite.FSObject import FSObject

def parsePropertiesFile(fp, reparse):
    # do the actual parsing for _readFile
    
    file = open(fp, 'r')    # not 'rb', as this is a text file!
    try:
        lines = file.readlines()
    finally:
        file.close()

    map = []
    lino=0
        
    last_propname = None; last_proptype = None
    for line in lines:
        lino = lino + 1
        line = line.strip()

        if not line or line[0] == '#':
            continue
        try:
            try:
                propname, proptv = line.split(':',1)
                proptype, propvstr = proptv.split( '=', 1 )        
                propname = propname.strip()
                proptype = proptype.strip()
                propvstr = propvstr.strip()
            except ValueError:
                dvalue = map[-1]['default_value'][:]
                if last_proptype in ('lines', 'ulines'):
                    dvalue.append(line.strip())
                elif last_proptype in ('text', 'utext'):
                    dvalue = dvalue+'\n'+line.strip()
                else:
                    raise
                map[-1]['default_value'] = dvalue
                setattr(self, map[-1]['id'], dvalue)
                continue
                    
            converter = get_converter( proptype, lambda x: x )
            propvalue = converter( propvstr )
            # Should be safe since we're loading from
            # the filesystem.
            map.append({'id':propname,
                        'type':proptype,
                        'mode':'',
                        'default_value':propvalue,
                        })
            last_propname = propname
            last_proptype = proptype
        except:
            raise
            raise ValueError, ( 'Error processing line %s of %s:\n%s'
                              % (lino,fp,line) )
    
    return tuple(map)

class FSNewPropertiesObject (FSObject, PropertyManager):
    """FSPropertiesObjects simply hold properties."""

    meta_type = 'Filesystem Properties Object'

    manage_options = ({'label':'Customize', 'action':'manage_main'},)
    
    security = ClassSecurityInfo()

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = Globals.DTMLFile('custprops', _dtmldir)

    # Declare all (inherited) mutating methods private.
    security.declarePrivate('manage_addProperty')
    security.declarePrivate('manage_editProperties')
    security.declarePrivate('manage_delProperties')
    security.declarePrivate('manage_changeProperties')
    security.declarePrivate('manage_propertiesForm')
    security.declarePrivate('manage_propertyTypeForm')
    security.declarePrivate('manage_changePropertyTypes')

    security.declareProtected(ViewManagementScreens, 'manage_doCustomize')
    def manage_doCustomize(self, folder_path, RESPONSE=None):
        """Makes a ZODB Based clone with the same data.

        Calls _createZODBClone for the actual work.
        """
        # Overridden here to provide a different redirect target.

        FSObject.manage_doCustomize(self, folder_path, RESPONSE)

        if RESPONSE is not None:
            fpath = tuple(folder_path.split('/'))
            folder = self.restrictedTraverse(fpath)
            RESPONSE.redirect('%s/%s/manage_propertiesForm' % (
                folder.absolute_url(), self.getId()))
    
    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        # Create a Folder to hold the properties.
        obj = Folder()
        obj.id = self.getId()
        map = []
        for p in self._properties:
            # This should be secure since the properties come
            # from the filesystem.
            setattr(obj, p['id'], getattr(self, p['id']))
            map.append({'id': p['id'],
                        'type': p['type'],
                        'mode': 'wd',})
        obj._properties = tuple(map)

        return obj

    def _readFile(self, reparse):
        """Read the data from the filesystem.
        
        Read the file (indicated by expandpath(self._filepath), and parse the
        data if necessary.
        """
        fp = expandpath(self._filepath)

        prop_map = parsePropertiesFile(fp, reparse)
        for propdict in prop_map:
            setattr(self, propdict['id'], propdict['default_value'])
        self._properties = prop_map

    if Globals.DevelopmentMode:
        # Provide an opportunity to update the properties.
        def __of__(self, parent):
            self = Acquisition.ImplicitAcquisitionWrapper(self, parent)
            self._updateFromFS()
            return self


Globals.InitializeClass(FSNewPropertiesObject)

registerFileExtension('newprops', FSNewPropertiesObject)
registerMetaType('New Properties Object', FSNewPropertiesObject)
