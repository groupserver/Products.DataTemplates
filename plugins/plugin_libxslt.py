import libxslt, libxml2, StringIO, sys

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
        import sys

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
                stream = StringIO.StringIO(str(obj()))
                                                                                
        if not stream and os.access(uri, os.F_OK):
            #Hack because urllib breaks on Windows paths
            stream = open(uri)
        elif not stream:
            stream = urllib.urlopen(uri)
        return stream

def render(self, source_xml, content_type):
    """ Render document using libxslt.

    """
    import tempfile, os, StringIO

    # handle URI's as if they were in the ZODB
    resolver = UriResolver(self).resolve
    libxml2.setEntityLoader(resolver)
    
    styledoc = libxml2.parseDoc(self())
    style = libxslt.parseStylesheetDoc(styledoc)
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
        style.freeStylesheet()
        doc.freeDoc()
        result.freeDoc()

    return result_string

def register_plugin(plugin_registry):
    plugin_registry['http://iopen.co.nz/plugins/xslt/libxslt'] = ('libxslt',
                                                                   render)
