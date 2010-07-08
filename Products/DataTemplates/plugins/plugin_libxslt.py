# Copyright IOPEN Technologies Ltd., 2003-2006
# richard@iopen.net
#
# For details of the license, please see LICENSE.
#
# You MUST follow the rules in http://iopen.net/STYLE before checking in code
# to the head. Code which does not follow the rules will be rejected.  
#
import libxslt, libxml2, StringIO, sys, os, urllib, tempfile, md5
from threading import Lock
import logging, time
log = logging.getLogger('DataTemplates.plugins.pluginlibxslt')

# Turn caching of XSLT on or off. This is an order of magnitude faster,
# but unfortunately we can only _uncache_ at the moment by restarting.
cache_on = True
if not cache_on:
   log.warn("XSLT Cache is OFF. This may have severe performance consequences.")

_thread_lock = Lock()

if hasattr(libxslt.stylesheet, 'saveResultToString'):
    RENDERVIAFILE=0
else:
    RENDERVIAFILE=1
    sys.stderr.write('The libxslt plugin for the DataTemplate product '
                     'is using an old version of libxslt -- consider upgrading '
                     'to the latest version to avoid workarounds\n')
    sys.stderr.flush()

class UriResolver:                                       
    def __init__(self,context=None):
        self.context = context

    def resolve(self, uri, id, ctxt):
        stream = None
        if self.context:
            for pathpart in uri.split('/'):
                if pathpart in ['..','.','http:']:
                    # ignore these, acquisition will work anyway
                    continue
                obj = getattr(self.context, pathpart, None)
                # the new context is the object
                if obj:
                    self.context = obj
            if obj:
                stream = StringIO.StringIO(obj().encode(self.context.char_encoding))
                                                                                
        if not stream and os.access(uri, os.F_OK):
            #Hack because urllib breaks on Windows paths
            stream = open(uri)
        elif not stream:
            stream = urllib.urlopen(uri)
        return stream

xslt_cache = {}
def _render(self, source_xml, content_type):
    """ Render document using libxslt.

    """
    global xslt_cache
    # handle URI's as if they were in the ZODB
    resolver = UriResolver(self).resolve
    libxml2.setEntityLoader(resolver)
    
    stylesheet = self()
    key = self.absolute_url(1)
    if cache_on and xslt_cache.has_key(key):
        style = xslt_cache[key]
    else:
        styledoc = libxml2.parseDoc(stylesheet)
        style = libxslt.parseStylesheetDoc(styledoc)
        if cache_on:
            xslt_cache[key] = style    
    
    doc = libxml2.parseDoc(source_xml)
    result = style.applyStylesheet(doc, None)
            
    result_string = ''
    try:
        if not RENDERVIAFILE:
            result_string = style.saveResultToString(result)
        else:
            # this is how we have to do things prior to the
            # 1.0.21 release of libxslt, a pretty horrible hack
            fn = tempfile.mktemp()
            style.saveResultToFilename(fn, result, 0)

            f = file(fn)
            result_string = f.read()
            f.close()
            os.remove(fn)
    finally:
        if not cache_on:
            style.freeStylesheet()
        doc.freeDoc()
        result.freeDoc()
    
    return result_string

def render(self, source_xml, content_type):
    """ Render document using libxslt.

    """
    try:
        _thread_lock.acquire()
        return _render(self, source_xml, content_type)
    finally:
        _thread_lock.release()
    
def register_plugin(plugin_registry):
    plugin_registry['http://iopen.co.nz/plugins/xslt/libxslt'] = ('libxslt',
                                                                   render)
