import urllib, StringIO, os, sys
import cStringIO
StringIO = cStringIO

from Ft.Lib.Uri import BaseUriResolver
from Ft.Xml.Xslt import Processor,XmlWriter,HtmlWriter,StringWriter, \
     OutputParameters
from Ft.Xml import InputSource

# In 4Suite, every input source can have a resolver associated
# with it, so we just need to create one for use with Zope. This
# is a slightly modified version of Richard's ZBaseUriResolver
class ZBaseUriResolver(BaseUriResolver):

    def __init__(self,context=None):
        BaseUriResolver.__init__(self)
        self.context = context
    
    def resolve(self, uri):
        """Locates the object referred to in the URI.
        """
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
    """Render document using 4suite.

    """
    proc = Processor.Processor()
    resolver = ZBaseUriResolver(self)

    factory = InputSource.InputSourceFactory(resolver=resolver)
    source = factory.fromString(str(self()), self.absolute_url())
    proc.appendStylesheet(source)


    if content_type in ['text/xml','text/html']:
        writer = XmlWriter.XmlWriter(proc.outputParams,StringIO.StringIO())
    else:
        writer = StringWriter.StringWriter(proc.outputParams,
                                           StringIO.StringIO())

    # Apply the stylesheet to the XMLTemplate. The result is
    # written to the output stream attribute of the writer so
    # grab that and send it back to the caller.
    proc.run(factory.fromString(source_xml),writer=writer)

    return writer.getStream().getvalue()

def register_plugin(plugin_registry):
    """Register the 4Suite plugin.
    """
    plugin_registry['http://iopen.co.nz/plugins/xslt/4suite_1_0a1'] = ('4Suite_1_0a1',
                                                                       render)

