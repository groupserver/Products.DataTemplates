# Copyright IOPEN Technologies Ltd., 2003
# richard@iopen.net
#
# For details of the license, please see LICENSE.
#
# You MUST follow the rules in README_STYLE before checking in code
# to the head. Code which does not follow the rules will be rejected.  
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
