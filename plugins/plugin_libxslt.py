import libxslt, libxml2, StringIO

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

    resolver = UriResolver(self).resolve
    libxml2.setEntityLoader(resolver)
    styledoc = libxml2.parseDoc(self())
    style = libxslt.parseStylesheetDoc(styledoc)
    doc = libxml2.parseDoc(source_xml)
    result = style.applyStylesheet(doc, None)
    outfile = StringIO.StringIO()
    fn = tempfile.mktemp()
    style.saveResultToFilename(fn, result, 0)
    style.freeStylesheet()
    doc.freeDoc()
    result.freeDoc()

    f = file(fn)
    result = f.read()
    f.close()
    os.remove(fn)

    return result

def register_plugin(plugin_registry):
    plugin_registry['http://iopen.co.nz/plugins/xslt/libxslt'] = ('libxslt',
                                                                   render)
