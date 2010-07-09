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
from Products.FileSystemSite.FSPageTemplate import FSPageTemplate
from Products.PageTemplates.ZopePageTemplate import Src

from Products.FileSystemSite.DirectoryView import registerFileExtension, expandpath
from Products.FileSystemSite.FSObject import FSObject

from Products.DataTemplates.XSLTTemplate import XSLTTemplate
from AccessControl.class_init import InitializeClass
class FSXSLTTemplate(FSPageTemplate, XSLTTemplate):
    """ A Page Template based framework for XSLT. The resulting XSLT is
        capable of rendering an XML document, when appropriately called.
        
    """
    meta_type = "XSLT Template"
    
    def __init__(self, id, filepath, fullname=None, properties=None):
        """ Initialise a new instance of XSLTTemplate.
        
        """
        FSObject.__init__(self, id, filepath, fullname, properties)
        self.ZBindings_edit(self._default_bindings)
        self.__name__ = id
        self.title = id
        self.id = id
        self._setPropValue("content_type", "text/xml")

    def _readFile(self, reparse):
        fp = expandpath(self._filepath)
        file = open(fp, 'r')    # not 'rb', as this is a text file!
        try:
            data = file.read()
        finally:
            file.close()
        if reparse:
            self.content_type = 'text/xml'
            self.write(data)
        
d = FSXSLTTemplate
o = Src()
setattr(d, 'source.xml', o)
setattr(d, 'source.html', o)

InitializeClass(FSXSLTTemplate)

registerFileExtension('xsl', FSXSLTTemplate)
registerFileExtension('xslt', FSXSLTTemplate)
#registerMetaType('XSLT Template', FSXSLTTemplate)
