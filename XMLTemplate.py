# Copyright IOPEN Technologies Ltd., 2003
# richard@iopen.net
#
# For details of the license, please see LICENSE.
#
# You MUST follow the rules in README_STYLE before checking in code
# to the head. Code which does not follow the rules will be rejected.  
#
import os, Globals

from Products.PageTemplates import ZopePageTemplate, PageTemplateFile
from AccessControl import getSecurityManager, ClassSecurityInfo
from DTCacheManager import DTCacheManagerAware

class XMLTemplate(ZopePageTemplate.ZopePageTemplate,
                  DTCacheManagerAware):
    """ An XML document that may use TAL and METAL to produce itself.

    As a side-effect, the document is also self-validating, thanks to
    the inheriting from PageTemplates.
    
    """
    security = ClassSecurityInfo()
    
    unselected_xslt = 'do not use xslt'
    unselected_schema = 'do not use schema'
    meta_type = "XML Template"

    version = 1.12

    render_methods = ['xml', 'html', 'pdf']
    content_type_map = {'xml': 'text/xml',
                        'html': 'text/html',
                        'pdf': 'application/pdf'}

    cache_manager = DTCacheManagerAware.null_cache_manager

    default_render_method = ''
    stylesheet_paths = []
    schema_paths = []
    _def_properties = ({'id': 'title', 'type': 'string', 'mode': 'w'},
                       {'id':'cache_manager', 'type': 'selection', 'mode':'w',
                        'select_variable': 'get_cacheManagerIds'},
                       {'id':'default_render_method', 'type': 'selection',
                        'mode': 'w', 'select_variable': 'get_renderMethods'},
                       {'id':'stylesheet_paths', 'type': 'lines', 'mode': 'w'},
                       {'id':'schema_paths', 'type': 'lines', 'mode': 'w'}
                       )
    _properties = _def_properties
    
    def __init__(self, id, file=None):
        """ Initialise a new instance of XMLTemplate.

        """
        self.__name__ = id
        self.title = id
        self.id = id
        
        self._setPropValue('content_type', 'text/xml')

        self.setup_xsltProperties()
        self.setup_schemaProperties()

        ZopePageTemplate.ZopePageTemplate.__init__(self, id)

        if hasattr(file, 'read'):
            self.write(file.read())

    def upgrade(self):
        """ Upgrade to the latest version.

        """
        currversion = getattr(self, '_version', 0)
        if currversion == self.version:
            return 'already running latest version (%s)' % currversion

        self._properties = self._def_properties
        self.setup_xsltProperties()
        self.setup_schemaProperties()

        self._version = self.version
        
        return 'upgraded %s to version %s from version %s' % (self.getId(),
                                                              self._version,
                                                              currversion)
    def setup_xsltProperties(self):
        """ Setup the various XSLT properties.
        
        """
        for method in self.render_methods:
            curr = getattr(self, 'xslt_%s' % method, '')
            try:
                self._delProperty('xslt_%s' % method)
            except ValueError:
                pass
            try:
                delattr(self, 'xslt_%s' % method)
            except:
                pass
            setattr(self, 'xslt_%s' % method, curr)

        properties = list(self._properties)
        for method in self.render_methods:
            properties.append({'id': 'xslt_%s' % method,
                               'type': 'selection',
                               'select_variable': 'get_templateCandidates',
                               'mode': 'w'})

        self._properties = tuple(properties)

    def setup_schemaProperties(self):
        """ Setup the various XML schema properties.

        """

        propname = 'xml_schema'
        curr = getattr(self, propname, '')
        try:
            self._delProperty(propname)
        except ValueError:
            pass
        try:
            delattr(self, propname)
        except:
            pass
        setattr(self, propname, curr)

        properties = list(self._properties)
        properties.append({'id': propname,
                               'type': 'selection',
                               'select_variable': 'get_schemaCandidates',
                               'mode': 'w'})

        self._properties = tuple(properties)

    def om_icons(self):
        """ Return a list of icon URLs to be displayed by an ObjectManager.
        
        """
        icons = ({'path': 'misc_/DataTemplates/ic-xml.gif',
                  'alt': self.meta_type, 'title': self.meta_type},)
        if not self._v_cooked:
            self._cook()
        if self._v_errors:
            icons = icons + ({'path': 'misc_/PageTemplates/exclamation.gif',
                              'alt': 'Error',
                              'title': 'This template has an error'},)
        return icons
    
    def get_renderMethods(self):
        """ Get the available render methods.
        
        """
        return self.render_methods

    #
    # XPath Methods
    #
    def xpath(self, expr=''):
        """ Return the snippets corresponding to the given xpath query.
                    
        """
        import xml
        try:
            from xml import xpath
        except ImportError:
            from Ft.Xml import XPath as xpath

        dom = self.get_dom(self(method='xml'))
        context = xpath.Context.Context(dom,
                                        processorNss=xml.dom.ext.GetAllNs(dom.documentElement))
        return xpath.Evaluate(expr, context=context)

    def xpath_as_xml(self, expr=''):
        """ Return the snippets corresponding to the xpath query as a list
            of XML strings.
        
        """
        results = []
        for result in self.xpath(expr):
            if result:
                results.append(result.toxml())
        
        return results

    def xpath_as_string(self, expr=''):
        """ Return the snippets corresponding to the xpath query as a single
            contiguous string, even if that means that the result isn't valid
            XML.
        
        """
        return ''.join(self.xpath_as_xml(expr))

    def _get_path_objs(self, path_list):
        """ Return the objects corresponding to the specified path list
        
        """
        objs = []
        for path in path_list:
            obj = self.unrestrictedTraverse(path, None)
            if obj and obj.meta_type == 'Folder':
                objs.append(obj)
        
        return objs

    def get_templateCandidates(self, include_unselected=1):
        """ Return a tuple of XSLT Containers available for us
        to render against.
        
        Optionally specify whether we want the unselected candidate
        option to be included.
        
        """
        vals = []
        
        if include_unselected:
            vals.append(self.unselected_xslt)
        for item in self.superValues('XSLT Template'):
            vals.append(item.id)
        
        for obj in self._get_path_objs(self.stylesheet_paths):
            for item in obj.superValues('XSLT Template'):
                vals.append(item.id)

        return tuple(vals)

    def get_schemaCandidates(self, include_unselected=1):
        """ Return a tuple of schema Containers available for us
        to validate against.

        Optionally specify whether we want the unselected candidate
        option to be included.
        
        """
        vals = []
        
        if include_unselected:
            vals.append(self.unselected_schema)

        #for item in self.superValues('XML Template'):
        #    vals.append(item.id)
        
        for obj in self._get_path_objs(self.schema_paths):
            for item in obj.superValues('XML Template'):
                vals.append(item.id)
        
        return tuple(vals)

    def write(self, text, pretty_print=0):
        """ Conveniently exposes the 'write' method provided by
        ZopePageTemplate.
        
        """
        # Don't raise any expat exceptions from the pretty printing, we
        # need to catch these later so they can be returned to the
        # interface
        if pretty_print:
            try:
                text = self.pretty_print(text)
            except:
                pass
        
        ZopePageTemplate.ZopePageTemplate.write(self, text)

    def writeFromHTTPPost(self, REQUEST, RESPONSE=None):
        """ Writes the raw POST data to the template.
        
        This is implemented specifically for accepting POSTs from
        the bitflux editor, hence the specific response codes.
        """
        # Retrieve the template text from the raw form data and call the
        # the PageTemplate write method with this text.
        try:
            REQUEST.stdin.seek(0)
            text = REQUEST.stdin.read()
            
            if len(text) > 0:
                self.write(text)
            
            # respond to the caller an XML stream indicating the result
            # of the call
            if RESPONSE:
                RESPONSE.setHeader('content-type', 'text/xml')
                RESPONSE.write('<save status="ok"/>')
            return 1
        except:
            if RESPONSE:
                RESPONSE.setHeader('context-type', 'text/xml')
                RESPONSE.write('<save status="failed"/>')
            return 0
        
    def get_dom(self, text):
        """ Return the DOM for the given XML.
        
        """
        from xml.dom import minidom
        
        dom = minidom.parseString(text)
        
        return dom
    
    def pretty_print(self, text):
        """ Pretty print the XML.
        
        """
        from xml.dom.ext import PrettyPrint
        from StringIO import StringIO
        
        dom = self.get_dom(text)
        
        stream = self.StringIO()
        PrettyPrint(dom, stream)
        
        dom.unlink()
        
        return stream.getvalue()
        
    def _render_as(self, extra_context={}, RESPONSE=None):
        """ Render the document via the given method.
        
        """
        import urlparse, md5
        
        request = getattr(self, 'REQUEST', None)
        
        method = None
        if extra_context.has_key('options') and extra_context['options'].has_key('method'):
            method = extra_context['options']['method']
        elif request.has_key('method'):
            method = request['method']
                
        if method not in self.render_methods:
            method = self.default_render_method
        
        xslt_id = getattr(self, 'xslt_%s' % method, '')
        
        content_type = self.content_type_map.get(method, 'text/plain')
        # note we make sure we don't have a unicode object at the later steps, because that causes
        # all sorts of headaches with the XML parser later
        xml_rendered = str(self.pt_render(extra_context=extra_context))
        if not xslt_id or xslt_id == self.unselected_xslt:
            rendered = xml_rendered
        else:
            xslt = getattr(self, xslt_id, None)
            if not xslt:
                for obj in self._get_path_objs(self.stylesheet_paths):
                    xslt = getattr(obj, xslt_id, None)
                    if xslt:
                        break
                    
            self.prune_cache()
            cached = self.retrieve_cache(xslt, xml_rendered)
            if cached:
                rendered = cached
            else:
                rendered = xslt.render_xml(xml_rendered, content_type)
                self.update_cache(xslt, xml_rendered, rendered, 0)
            
        # set the base properly
        pathparts = list(urlparse.urlparse(self.absolute_url()))
        base = os.path.split(pathparts[2])[0]
        pathparts[2] = base
        base = urlparse.urlunparse(pathparts)
        
        RESPONSE.setBase(base)
        RESPONSE.setHeader('Content-Type', content_type)
        
        return rendered

    def _exec(self, bound_names, args, kw):
        """ Call a Data Template.
            
        A good deal of this code is 'borrowed' directly from
        the ZopePageTemplate code from which this inherits.
        
        In addition to the parameters normally recognised by a
        ZopePageTemplate, a 'method' parameter may also be passed,
        which should match one of the defined 'render_methods' in
        order to change the type of output produced.
        
        """
        if not kw.has_key('args'):
            kw['args'] = args
        bound_names['options'] = kw
        
        try:
            response = self.REQUEST.RESPONSE
            if not response.headers.has_key('content-type'):
                response.setHeader('content-type', self.content_type)
        except AttributeError:
            pass
        
        security = getSecurityManager()
        bound_names['user'] = security.getUser()
        
        # Retrieve the value from the cache.
        keyset = None
        if self.ZCacheable_isCachingEnabled():
            # Prepare a cache key.
            keyset = {'here': self._getContext(),
                      'bound_names': bound_names}
            result = self.ZCacheable_get(keywords=keyset)
            if result is not None:
                # Got a cached value.
                return result

        # Execute the template in a new security context.
        security.addContext(self)
        try:
            result = self._render_as(extra_context=bound_names,
                                     RESPONSE=response)
            if keyset is not None:
                # Store the result in the cache.
                self.ZCacheable_set(result, keywords=keyset)
            return result
        finally:
            security.removeContext(self)

#
# Zope Management Methods
#
manage_addXMLTemplateForm = PageTemplateFile.PageTemplateFile(
    'management/manage_addXMLTemplateForm.zpt',
    globals(), __name__='manage_addXMLTemplateForm')

def manage_addXMLTemplate(self, id, file, 
                                REQUEST=None, RESPONSE=None, submit=None):
    """ Add a new instance of XMLTemplate.
        
    """
    if not id and file:
        id = file.filename
    obj = XMLTemplate(id, file)
    self._setObject(id, obj)
    
    if RESPONSE and submit:
        if submit.strip().lower() == 'add':
            RESPONSE.redirect('%s/manage_main' % self.DestinationURL())
        else:
            RESPONSE.redirect('%s/manage_main' % id)

def initialize(context):
    context.registerClass(
        XMLTemplate,
        permission='Add XML Template',
        constructors=(manage_addXMLTemplateForm,
                      manage_addXMLTemplate),
        icon='icons/ic-xml.gif'
        )
