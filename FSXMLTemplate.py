# Copyright (C) 2003,2004 IOPEN Technologies Ltd.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# You MUST follow the rules in http://iopen.net/STYLE before checking in code
# to the trunk. Code which does not follow the rules will be rejected.
#
import Globals

from Products.FileSystemSite.FSPageTemplate import FSPageTemplate

from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate, Src

from Products.FileSystemSite.DirectoryView import registerFileExtension, expandpath
from Products.FileSystemSite.FSObject import FSObject
from FSNewPropertiesObject import parsePropertiesFile

class TransformError(Exception):
    pass

from Products.DataTemplates.XMLTemplate import XMLTemplate
class FSXMLTemplate(FSPageTemplate, ZopePageTemplate, XMLTemplate):
    """ An XML document that may use TAL and METAL to produce itself.

    As a side-effect, the document is also self-validating, thanks to
    the inheriting from PageTemplates.
    
    """
    meta_type = "XML Template"
        
    def __init__(self, id, filepath, fullname, properties):
        """ Initialise a new instance of XMLTemplate.

        """
        FSObject.__init__(self, id, filepath, fullname, properties)
        self.ZBindings_edit(self._default_bindings)
        
        self.__name__ = id
        self.title = id
        self.id = id
        
        self._setPropValue('content_type', 'text/xml')

        self.setup_transformProperties()
        self.setup_schemaProperties()
        
        try:
            fp = expandpath(self._filepath+'.propsheet')
            prop_map = parsePropertiesFile(fp, 1)
            for propdict in prop_map:
                setattr(self, propdict['id'], propdict['default_value'])
            self._properties = prop_map
        except:
            raise
        
        ZopePageTemplate.__init__(self, id)            

    def inZODB(self):
        """ """
        self._readFile(1)
        self.customising = True
        
    def _readFile(self, reparse):
        if getattr(self, 'customising', False):
            return
            
        fp = expandpath(self._filepath)
        file = open(fp, 'r')    # not 'rb', as this is a text file!
        try:
            data = file.read()
        finally:
            file.close()
        if reparse:
            self.content_type = 'text/xml'
            self.write(data)

    def _exec(self, bound_names, args, kw):
        """ Call an FS XML Template by calling the underlying Data Template
        method.
        
        """
        return XMLTemplate._exec(self, bound_names, args, kw)

d = FSXMLTemplate
o = Src()
setattr(d, 'source.xml', o)
setattr(d, 'source.html', o)

Globals.InitializeClass(FSXMLTemplate)

registerFileExtension('xml', FSXMLTemplate)
registerMetaType('XML Template', FSXMLTemplate)
registerFileExtension('xml', FSXMLTemplate)


