# we can't use cStringIO because it's not unicode compliant
import urllib, StringIO, os, sys
import cStringIO
StringIO = cStringIO
#
# override some methods because Zope has no fucking way
# to get the context globally.
# Yes, I am pissed off.
#
from Ft.Lib.Uri import BaseUriResolver
class ZBaseUriResolver(BaseUriResolver):
    def resolve(self, uri, base='', context=None):
        import sys
        sys.stdout.write('resolve\n'); sys.stdout.flush()
        uri = self.normalize(uri, base)
        stream = None
        if context:
            for pathpart in uri.split('/'):
                if pathpart == '..' or pathpart == '.':
                    # ignore these, acquisition will work anyway
                    continue
                obj = getattr(context, pathpart, None)
                # the new context is the object
                if obj:
                    context = obj
            if obj:
                stream = StringIO.StringIO(obj.pt_render())
        if not stream and os.access(uri, os.F_OK):
            #Hack because urllib breaks on Windows paths
            stream = open(uri)
        elif not stream:
            stream = urllib.urlopen(uri)
        sys.stdout.flush()
        return stream

from Ft.Lib import ReaderBase
def fromUri(self, uri, baseUri='', ownerDoc=None, stripElements=None,
            context=None):
    "Create a DOM from a URI"
    self.uriResolver = ZBaseUriResolver()
    stream = self.uriResolver.resolve(uri, baseUri, context)
    newBaseUri = self.uriResolver.normalize(uri, baseUri)
    rt = self.fromStream(stream, newBaseUri, ownerDoc, stripElements)
    stream.close()
    return rt

ReaderBase.DomletteReader.fromUri = fromUri

from xml.xslt.StylesheetReader import StylesheetReader
from xml.xslt.Processor import Processor
class ZStylesheetReader(StylesheetReader):
    def __init__(self, resolveEntity=None, processIncludes=1,
                 visitedHrefs=None, force8Bit=0, extModules=None,
                 stylesheetIncPaths=None, context=None):
        self.__initargs = (resolveEntity, processIncludes,
                           visitedHrefs, force8Bit, extModules,
                           stylesheetIncPaths, context)
	self._context = context
        StylesheetReader.__init__(self, resolveEntity=None, processIncludes=1,
                 visitedHrefs=None, force8Bit=0, extModules=None,
                 stylesheetIncPaths=None)

    def __getinitargs__(self):
        return self.__initargs

    def fromUri(self, uri, baseUri='', ownerDoc=None, stripElements=None,
                importIndex=0, importDepth=0):
        self._importIndex = importIndex
        self._importDepth = importDepth
        save_sheet_uri = self._ssheetUri
        self._ssheetUri = urllib.basejoin(baseUri, uri)
        result = ReaderBase.DomletteReader.fromUri(self, uri, baseUri,
                                                   ownerDoc, stripElements,
                                                   context=self._context)
        self._ssheetUri = save_sheet_uri
        return result
#
# end of stupid fucking crap
#
