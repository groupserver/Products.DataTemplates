# Copyright IOPEN Technologies Ltd., 2003
# richard@iopen.net
#
# For details of the license, please see LICENSE.
#
# You MUST follow the rules in README_STYLE before checking in code
# to the head. Code which does not follow the rules will be rejected.  
#
import reportlab.lib.utils, xml
from trml2pdf import trml2pdf

import ThreadLock
 
_thread_lock = ThreadLock.allocate_lock()

class RMLPluginError(Exception):
    pass

def _rml_doc__init__(self, data, context):
    self.dom = xml.dom.minidom.parseString(data)
    self.context = context
    self.filename = self.dom.documentElement.getAttribute('filename')
trml2pdf._rml_doc.__init__ = _rml_doc__init__

def _rml_doc_render(self, out):
    el = self.dom.documentElement.getElementsByTagName('stylesheet')
    self.styles = trml2pdf._rml_styles(el, self.context)
    
    el = self.dom.documentElement.getElementsByTagName('template')
    if len(el):
        pt_obj = trml2pdf._rml_template(out, el[0], self)
        pt_obj.render(self.dom.documentElement.getElementsByTagName('story')[0])
    else:
        self.canvas = trml2pdf.canvas.Canvas(out)
        pd = self.dom.documentElement.getElementsByTagName('pageDrawing')[0]
        pd_obj = trml2pdf._rml_canvas(self.canvas, None, self)
        pd_obj.render(pd)
        self.canvas.showPage()
        self.canvas.save()
trml2pdf._rml_doc.render = _rml_doc_render

def _rml_styles__init__(self, nodes, context):
    self.context = context
    self.styles = {}
    self.names = {}
    self.table_styles = {}
    for node in nodes:
        for style in node.getElementsByTagName('blockTableStyle'):
            self.table_styles[style.getAttribute('id')] = self._table_style_get(style)
        for style in node.getElementsByTagName('paraStyle'):
            self.styles[style.getAttribute('name')] = self._para_style_get(style)
        for variable in node.getElementsByTagName('initialize'):
            for name in variable.getElementsByTagName('name'):
                self.names[ name.getAttribute('id')] = name.getAttribute('value')
trml2pdf._rml_styles.__init__ = _rml_styles__init__

def _image(self, node):
    from reportlab.lib.utils import ImageReader
    from trml2pdf import utils
    img = ImageReader(str(node.getAttribute('file')), self.doc.context)
    (sx,sy) = img.getSize()
    args = {}
    for tag in ('width','height','x','y'):
        if node.hasAttribute(tag):
            args[tag] = utils.unit_get(node.getAttribute(tag))
        if ('width' in args) and (not 'height' in args):
            args['height'] = sy * args['width'] / sx
        elif ('height' in args) and (not 'width' in args):
            args['width'] = sx * args['height'] / sy
        elif ('width' in args) and ('height' in args):
            if (float(args['width'])/args['height'])>(float(sx)>sy):
                args['width'] = sx * args['height'] / sy
            else:
                args['height'] = sy * args['width'] / sx
    self.canvas.drawImage(img, **args)
trml2pdf._rml_canvas._image = _image

def ImageReader__init__(self, fileName, context):
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
        obj = getattr(context, pathpart, None)
        # the new context is the object
        if obj:
            context = obj
    if obj:
        data = StringIO.StringIO(obj.data)
        size = (obj.width, obj.height)    
        self._image = PIL.Image.open(PIL.ImageFileIO.ImageFileIO(data))
    else:
        raise RMLPluginError, 'Image %s could not be found' % fileName
reportlab.lib.utils.ImageReader.__init__ = ImageReader__init__

def render(self, source_xml, content_type):
    """ Render document using trml2pdf.

    """
    import StringIO
    
    fp = StringIO.StringIO()
    try:
        # numerous issues were encountered with multiple thread accesses
        # so we're going for absolute robustness
        _thread_lock.acquire()
        r = trml2pdf._rml_doc(source_xml, self)
        r.render(fp)
    finally:
        _thread_lock.release()

    return fp.getvalue()
    
def register_plugin(plugin_registry):
    plugin_registry['http://iopen.co.nz/plugins/rml/trml2pdf'] = ('trml2pdf',
                                                                   render)

