# Copyright (C) 2003,2004 IOPEN Technologies Ltd.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# You MUST follow the rules in http://iopen.net/STYLE before checking in code
# to the trunk. Code which does not follow the rules will be rejected.
#

# we can't use cStringIO because it's not unicode compliant
import urllib, StringIO, os, sys
import cStringIO
#StringIO = cStringIO
#
# override some methods because Zope has no fucking way
# to get the context globally.
# Yes, I am pissed off.
#
from Ft.Lib.Uri import BaseUriResolver
class ZBaseUriResolver(BaseUriResolver):
    def resolve(self, uri, base='', context=None):
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
                stream = StringIO.StringIO(obj().encode(context.char_encoding))
        if not stream and os.access(uri, os.F_OK):
            #Hack because urllib breaks on Windows paths
            stream = open(uri)
        elif not stream:
            stream = urllib.urlopen(uri)
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
