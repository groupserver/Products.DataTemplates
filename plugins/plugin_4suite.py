from xslthack import *
def render(self, source_xml, content_type):
    """ Render document using 4suite.

    """
    # we have to use StringIO not cStringIO because, at this time,
    # cStringIO isn't unicode aware :(
    import StringIO, xml
    
    proc = Processor()
    proc.setStylesheetReader(ZStylesheetReader(context=self))
    proc.appendStylesheetStream(StringIO.StringIO(str(self())))

    if content_type == 'text/xml':
        writer = xml.xslt.XmlWriter.XmlWriter(None)
    elif content_type == 'text/html':
        writer = xml.xslt.HtmlWriter.HtmlWriter(None)
    else:
        writer = xml.xslt.TextWriter.TextWriter(None)

    result = proc.runString(source_xml, writer=writer)

    return result

def register_plugin(plugin_registry):
    plugin_registry['http://iopen.co.nz/plugins/xslt/4suite'] = ('4Suite',
                                                                  render)

