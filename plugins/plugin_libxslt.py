def render(self, source_xml, content_type):
    """ Render document using libxslt.

    """
    import libxml2, libxslt, tempfile, os, StringIO
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
