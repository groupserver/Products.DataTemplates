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

