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
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('DataTemplates')

testXML = """<?xml version="1.0" ?>
<root>
  <testnode someattribute="foo">
    Some test text.
  </testnode>
  <emptynode anotherattribute="wibble"/>
</root>"""

class FakePOSTRequest:
    """ A really minimal class to fake a POST. Probably looks
    nothing like the real thing, but close enough for our needs :)
    
    """
    import StringIO
    stdin = StringIO.StringIO(testXML)

def minimallyEqualXML(one, two):
    """ Strip all the whitespace out of two pieces of XML code, having first converted
    them to a DOM as a minimal test of equivalence.
    
    """
    from xml.dom import minidom
    
    sf = lambda x: filter(lambda y: y.strip(), x)
    
    onedom = minidom.parseString(one)
    twodom = minidom.parseString(two)
    
    return sf(onedom.toxml()) == sf(twodom.toxml())

from Products.DataTemplates import XSLTTemplate
class TestXSLTTemplate(ZopeTestCase.ZopeTestCase):
    def afterSetUp(self):
        pass
        
    def afterClear(self):
        pass    

    def _setupXSLTTemplate(self):
        """ Create a new XSLT Template as the basis for our tests.
        
        """
        XSLTTemplate.manage_addXSLTTemplate(self.folder, 'xslt_template', None)
        return self.folder.xslt_template

    def testCreateXSLTTemplate(self):
        self._setupXSLTTemplate()
        self.failUnless(hasattr(self.folder, 'xslt_template'))

    def testWrite(self):
        from xml.dom import minidom
        
        xslt_template = self._setupXSLTTemplate()
        
        xslt_template.write(testXML)
        
        result = xslt_template()
        
        # convert into DOM and back again to get an equivalent interpretation of the XML
        self.failUnless(minidom.parseString(result).toxml() == minidom.parseString(testXML).toxml())

from Products.DataTemplates import XMLTemplate
class TestXMLTemplate(ZopeTestCase.ZopeTestCase):
    def afterSetUp(self):
        pass
        
    def afterClear(self):
        pass
    
    def _setupXMLTemplate(self):
        """ Create a new XML Template as the basis for our tests.
        
        """
        XMLTemplate.manage_addXMLTemplate(self.folder, 'xml_template', None)
        return self.folder.xml_template
        
    def testCreateXMLTemplate(self):
        self._setupXMLTemplate()
        self.failUnless(hasattr(self.folder, 'xml_template'))
        
    def testRenderMethods(self):
        xml_template = self._setupXMLTemplate()
        render_methods = xml_template.get_renderMethods()
        self.failUnless(type(render_methods) in (type([]), type(())))
        
    def testTemplateCandidatesNULL(self):
        """ Test the NULL case scenario, when no template candidates except
        default candidate should be returned.
            
        """
        xml_template = self._setupXMLTemplate()
        
        # should contain the unselected xslt
        template_candidates = xml_template.get_templateCandidates()
        self.failUnless(type(template_candidates) == type(()))
        self.failUnless(template_candidates == (xml_template.unselected_xslt,))
        
        # should be completely empty
        template_candidates = xml_template.get_templateCandidates(0)
        self.failUnless(type(template_candidates) == type(()))
        self.failIf(template_candidates)
        
    def testWrite(self):
        from xml.dom import minidom
        
        xml_template = self._setupXMLTemplate()
        
        xml_template.write(testXML)
        
        result = xml_template()
        
        # convert into DOM and back again to get an equivalent interpretation of the XML
        self.failUnless(minidom.parseString(result).toxml() == minidom.parseString(testXML).toxml())
    
    def testWriteFromPost(self):
        xml_template = self._setupXMLTemplate()
        
        fake_post_request = FakePOSTRequest()
        self.failUnless(xml_template.writeFromHTTPPost(REQUEST=fake_post_request))
        self.failUnless(minimallyEqualXML(xml_template(), testXML))
        
    def testGetDom(self):
        from xml.dom import minidom
        
        xml_template = self._setupXMLTemplate()
        dom = xml_template.get_dom(testXML)
        
        self.failUnless(isinstance(dom, minidom.Document))
    
    def testWriteWithPrettyPrint(self):
        from xml.dom import minidom
        
        xml_template = self._setupXMLTemplate()
        
        xml_template.write(testXML, 1)
        
        result = xml_template()
        
        # convert into DOM and back again to get an equivalent interpretation of the XML
        self.failUnless(minimallyEqualXML(result, testXML))

if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestXMLTemplate))
        return suite
