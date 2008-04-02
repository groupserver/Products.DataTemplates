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
import os, Globals
from Products.PageTemplates import ZopePageTemplate, PageTemplateFile
from AccessControl import ClassSecurityInfo
from DTCacheManager import DTCacheManagerAware

class XSLTPluginError(Exception):
    pass

class XSLTTemplate(ZopePageTemplate.ZopePageTemplate,
                   DTCacheManagerAware):
    """ A Page Template based framework for XSLT. The resulting XSLT is
        capable of rendering an XML document, when appropriately called.
        
    """
    security = ClassSecurityInfo()
    
    version = 1.11
    
    meta_type = "XSLT Template"

    char_encoding = 'UTF-8'

    unselected_xslt_render_plugin = 'do not render xslt'
    
    xslt_render_plugin = unselected_xslt_render_plugin
    _def_properties = ({'id': 'title', 'type': 'string', 'mode': 'w'},
                       {'id': 'xslt_render_plugin', 'type': 'selection',
                        'mode': 'w', 'select_variable': 'get_renderPluginIds'}
                       )
    _properties = _def_properties
    
    def __init__(self, id, file=None):
        """ Initialise a new instance of XSLTTemplate.
        
        """
        self.__name__ = id
        self.title = id
        self.id = id
        self._setPropValue("content_type", "text/xml")
        if hasattr(file, 'read'):
            self.write(file.read())
    
    def upgrade(self):
        """ Upgrade to the latest version.

        """
        currversion = getattr(self, '_version', 0)
        if currversion == self.version:
            return 'already running latest version (%s)' % currversion
        
        self._version = self.version
        self._properties = self._def_properties
        
        return 'upgraded %s to version %s from version %s' % (self.getId(),
                                                              self._version,
                                                              currversion)

    def om_icons(self):
        """Return a list of icon URLs to be displayed by an ObjectManager"""
        icons = ({'path': 'misc_/DataTemplates/ic-xsl.gif',
                  'alt': self.meta_type, 'title': self.meta_type},)
        if not self._v_cooked:
            self._cook()
        if self._v_errors:
            icons = icons + ({'path': 'misc_/PageTemplates/exclamation.gif',
                              'alt': 'Error',
                              'title': 'This template has an error'},)
        return icons

    def write(self, text, pretty_print=0):
        """ Conveniently exposes the 'write' method provided by
        ZopePageTemplate.
        
        """
        self.invalidate_cache()
        
        # Don't raise any expat exceptions from the pretty printing, we
        # need to catch these later so they can be returned to the
        # interface
        if pretty_print:
            try:
                text = self.pretty_print(text)
            except:
                pass
        
        ZopePageTemplate.ZopePageTemplate.write(self, text)

    def get_renderPlugins(self):
        """ Get the render plugins.
            
        """
        import plugins
        return plugins.plugin_registry

    def get_renderPluginIds(self):
        """ Get the render plugin ids.
        
        """
        ids = self.get_renderPlugins().keys()
        ids.sort()
        
        return [self.unselected_xslt_render_plugin]+ids

    def get_renderPluginByUri(self, uri):
        """ Get a render plugin by its uri.
        
        """
        render_plugins = self.get_renderPlugins()
        return render_plugins.get(uri, (None, None))[1]

    def get_currentRenderPlugin(self):
        """ Get the currently selected render plugin.
        
        """
        if self.xslt_render_plugin != self.unselected_xslt_render_plugin:
            return self.get_renderPluginByUri(self.xslt_render_plugin)
        return None

    def render_xml(self, source_xml, content_type='text/plain'):
        """ Given an XML document, render it using our XSL Template.
        
        """
        import sys
        render_plugin = self.get_currentRenderPlugin()
        if render_plugin:
            result = render_plugin(self, source_xml, content_type)
        else:
            raise XSLTPluginError("No plugin found to render XML content")
	
        return result

    def index_html(self, RESPONSE):
        """ Return the raw XSLT content.
        
        """
        RESPONSE.setHeader('Content-Type', 'text/xml')
        
        return self.pt_render()

#
# Zope Management Methods
#
manage_addXSLTTemplateForm = PageTemplateFile.PageTemplateFile(
    'management/manage_addXSLTTemplateForm.zpt',
    globals(), __name__='manage_addXSLTTemplateForm')

def manage_addXSLTTemplate(self, id, file,
                                 REQUEST=None, RESPONSE=None, submit=None):
    """ Add a new instance of XSLTTemplate.

    """
    if not id and file:
        id = file.filename
    obj = XSLTTemplate(id, file)
    self._setObject(id, obj)

    if RESPONSE and submit:
        if submit.strip().lower() == 'add':
            RESPONSE.redirect('%s/manage_main' % self.DestinationURL())
        else:
            RESPONSE.redirect('%s/manage_main' % id)

def initialize(context):
    context.registerClass(
        XSLTTemplate,
        permission='Add XSLT Template',
        constructors=(manage_addXSLTTemplateForm,
                      manage_addXSLTTemplate),
        icon='icons/ic-xsl.gif'
        )
