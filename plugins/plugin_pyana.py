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
# You MUST follow the rules in STYLE before checking in code
# to the trunk. Code which does not follow the rules will be rejected.
#
import Pyana, StringIO, sys, os, urllib, tempfile
from zLOG import LOG, WARNING
class StringSource:
    def __init__(self, string):
        self.string = string
    
    def makeStream(self):
        return StringIO.StringIO(str(self.string))

class UriResolver:                                                                   
    def __init__(self, context=None, reportExceptions=1):
        self.reportExceptions = reportExceptions
        self.context = context

    def resolveEntity(self, public, system):
        stream = None
        if self.context:
            for pathpart in system.split('/'):
                if pathpart in ['..','.','http:', 'ftp:', 'file:']:
                    # ignore these, acquisition will work anyway
                    continue
                obj = getattr(self.context, pathpart, None)
                # the new context is the object
                if obj:
                    self.context = obj
            if obj:
                stream = StringSource(str(obj()))
                                                                                
        if not stream and os.access(uri, os.F_OK):
            #Hack because urllib breaks on Windows paths
            stream = open(system)
        elif not stream:
            stream = urllib.urlopen(system)
        return stream

def render(self, source_xml, content_type):
    """ Render document using libxslt.
    
    """
    # handle URI's as if they were in the ZODB
    t = Pyana.Transformer()
    resolver = UriResolver(self)
    
    t.setEntityResolver(resolver)
    
    return t.transform2String(StringSource(source_xml), StringSource(self()))
    
def register_plugin(plugin_registry):
    plugin_registry['http://iopen.co.nz/plugins/xslt/pyana'] = ('pyana',
                                                                render)
