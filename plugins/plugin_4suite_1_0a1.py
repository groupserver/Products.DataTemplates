
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
                stream = StringIO.StringIO(obj.pt_render())
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
    source = InputSource.InputSource(StringIO.StringIO(self.pt_render()),
                                     self.absolute_url(),resolver=resolver)
    proc.appendStylesheet(source)

    opts = OutputParameters.OutputParameters()
    # opts.indent = 0

    if content_type == 'text/xml':
        writer = XmlWriter.XmlWriter(opts,StringIO.StringIO())
    elif content_type == 'text/html':
        writer = HtmlWriter.HtmlWriter(opts,StringIO.StringIO())
    else:
        writer = StringWriter.StringWriter(opts,StringIO.StringIO())

    # Apply the stylesheet to the XMLTemplate. The result is
    # written to the output stream attribute of the writer so
    # grab that and send it back to the caller.
    proc.run(InputSource.InputSource(StringIO.StringIO(source_xml),
                                     resolver=resolver),
             writer=writer)

    return writer.getStream().getvalue()


def register_plugin(plugin_registry):
    """Register the 4Suite plugin.
    """
    plugin_registry['http://iopen.co.nz/plugins/xslt/4suite_1_0a1'] = ('4Suite_1_0a1',
                                                                       render)

