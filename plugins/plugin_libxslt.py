import libxslt, libxml2
def render(self, source_xml, content_type):
    """ Render document using libxslt.

    """
    import tempfile, os, StringIO
    styledoc = libxml2.parseDoc(self.pt_render())
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
