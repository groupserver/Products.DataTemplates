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
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from AccessControl import ClassSecurityInfo
from Products.PageTemplates import PageTemplateFile
from XMLTemplate import TransformError

class RMLRenderer(SimpleItem, PropertyManager):
    """ A handler for RML as part of the DataTemplate system. The resulting RML is
        capable of rendering RML content into the final presentation, when
        appropriately called.
        
        Optionally, transforms an XML document can be transformed into RML 
        with an XSLT Template first.
        
        The plugin chosen controls how the content is rendered.
        
    """
    security = ClassSecurityInfo()
    
    version = 0.9
    
    meta_type = "RML Renderer"
    
    unselected_rml_render_plugin = 'do not render rml'
    unselected_stylesheet = 'do not use stylesheet'
    
    stylesheet_container_types = ('XSLT Template',)
    stylesheet_paths = []
    stylesheet = []
    
    manage_options = PropertyManager.manage_options + \
                     SimpleItem.manage_options
    
    rml_render_plugin = unselected_rml_render_plugin
    _def_properties = ({'id': 'title', 'type': 'string', 'mode': 'w'},
                       {'id':'stylesheet_paths', 'type': 'lines', 'mode': 'w'},
                       {'id': 'rml_render_plugin', 'type': 'selection',
                        'mode': 'w', 'select_variable': 'get_renderPluginIds'},
                       {'id': 'stylesheet',
                        'type': 'selection',
                        'select_variable': 'get_templateCandidates',
                        'mode': 'w'}
                       )
    
    _properties = _def_properties
    
    def __init__(self, id):
        """ Initialise a new instance of RMLRenderer.
        
        """
        self.__name__ = id
        self.title = id
        self.id = id
        
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
        
    def get_renderPlugins(self):
        """ Get the render plugins.
            
        """
        import rmlplugins
        return rmlplugins.plugin_registry

    def get_renderPluginIds(self):
        """ Get the render plugin ids.
        
        """
        ids = self.get_renderPlugins().keys()
        ids.sort()
        
        return [self.unselected_rml_render_plugin]+ids

    def get_renderPluginByUri(self, uri):
        """ Get a render plugin by its uri.
        
        """
        render_plugins = self.get_renderPlugins()
        return render_plugins.get(uri, (None, None))[1]

    def get_currentRenderPlugin(self):
        """ Get the currently selected render plugin.
        
        """
        if self.rml_render_plugin != self.unselected_rml_render_plugin:
            return self.get_renderPluginByUri(self.rml_render_plugin)
        return None
        
    def _get_path_objs(self, path_list):
        """ Return the objects corresponding to the specified path list
        
        """
        objs = []
        for path in path_list:
            obj = self.unrestrictedTraverse(path, None)
            if obj and getattr(obj, 'isPrincipiaFolderish', 0):
                objs.append(obj)
        
        return objs
        
    def get_templateCandidates(self, include_unselected=1):
        """ Return a tuple of Stylesheet Containers available for us
        to render against.
        
        Optionally specify whether we want the unselected candidate
        option to be included.
        
        """
        vals = []
        objs = list(self.superValues(self.stylesheet_container_types))
        for path in self._get_path_objs(self.stylesheet_paths):
            for item in path.superValues(self.stylesheet_container_types):
                objs.append(item)
                
        for obj in objs:
            mtype = obj.meta_type.lower().replace('template','').strip()
            vals.append('%s (%s)' % (obj.id, mtype))
        
        vals.sort()
        if include_unselected:
            vals.insert(0, self.unselected_stylesheet)
            
        return tuple(vals)
        
    def render_xml(self, source_xml, content_type='text/plain'):
        """ Given an XML document, render it using our RML Renderer.
        
        """
        import re
        
        stylesheet_id = getattr(self, 'stylesheet', '')
        stylesheet_id = re.sub('\s\([^\(]*?\)$', '', stylesheet_id)
        
        if not stylesheet_id or stylesheet_id == self.unselected_stylesheet:
            rendered = source_xml
        else:
            stylesheet = getattr(self, stylesheet_id, None)
            if not stylesheet:
                for obj in self._get_path_objs(self.stylesheet_paths):
                    stylesheet = getattr(obj, stylesheet_id, None)
                    if stylesheet:
                        break
            if not stylesheet:
                raise TransformError, 'Stylesheet %s did not exist' % stylesheet_id
            
            rendered = stylesheet.render_xml(source_xml, content_type)
            
        render_plugin = self.get_currentRenderPlugin()
        if render_plugin:
            result = render_plugin(self, rendered, content_type)
        else:
            result = ''

        return result
        
    def index_html(self, RESPONSE):
        """ Return the raw RML content.
        
        """
        RESPONSE.setHeader('Content-Type', 'text/xml')
        
        return self.pt_render()

#
# Zope Management Methods
#
manage_addRMLRendererForm = PageTemplateFile.PageTemplateFile(
    'management/manage_addRMLRendererForm.zpt',
    globals(), __name__='manage_addRMLRendererForm')

def manage_addRMLRenderer(self, id,
                                REQUEST=None, RESPONSE=None, submit=None):
    """ Add a new instance of RMLRenderer.

    """
    obj = RMLRenderer(id)
    self._setObject(id, obj)

    if RESPONSE and submit:
        if submit.strip().lower() == 'add':
            RESPONSE.redirect('%s/manage_main' % self.DestinationURL())
        else:
            RESPONSE.redirect('%s/manage_main' % id)

def initialize(context):
    context.registerClass(
        RMLRenderer,
        permission='Add RML Template',
        constructors=(manage_addRMLRendererForm,
                      manage_addRMLRenderer),
        icon='icons/ic-rml.gif'
        )
