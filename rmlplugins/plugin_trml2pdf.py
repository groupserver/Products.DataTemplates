# Copyright IOPEN Technologies Ltd., 2003
# richard@iopen.net
#
# For details of the license, please see LICENSE.
#
# You MUST follow the rules in README_STYLE before checking in code
# to the head. Code which does not follow the rules will be rejected.  
#
import reportlab.lib.utils
def imageReaderInit(self, fileName):
    import PIL.Image, PIL.ImageFileIO, StringIO
    self._fileName = fileName
    self._image = None
    self._width = None
    self._height = None
    self._transparent = None
    self._data = None
    
    for pathpart in fileName.split('/'):
        if pathpart == '..' or pathpart == '.':
            # ignore these, acquisition will work anyway
            continue
        obj = getattr(self.context, pathpart, None)
        # the new context is the object
        if obj:
            self.context = obj
    if obj:
        data = StringIO.StringIO(obj.data)
        size = (obj.width, obj.height)    
        self._image = PIL.Image.open(PIL.ImageFileIO.ImageFileIO(data))

def render(self, source_xml, content_type):
    """ Render document using trml2pdf.

    """
    import StringIO, trml2pdf

    reportlab.lib.utils.ImageReader.__init__ = imageReaderInit
    reportlab.lib.utils.ImageReader.context = self
    result = trml2pdf.parseString(source_xml)
    
    return result

def register_plugin(plugin_registry):
    plugin_registry['http://iopen.co.nz/plugins/rml/rml2pdf'] = ('rml2pdf',
                                                                  render)

