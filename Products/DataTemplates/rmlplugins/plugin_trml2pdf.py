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
import xml, types, copy, sys
from trml2pdf import trml2pdf

from threading import Lock 
_thread_lock = Lock()

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
                self.names[ name.gectAttribute('id')] = name.getAttribute('value')
trml2pdf._rml_styles.__init__ = _rml_styles__init__

class ImageReader:
    "Wraps up either PIL to get data from bitmaps"
    def __init__(self, fileName, context):
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
            # if we're given a function, call it to get the real Image
            if type(obj) == types.MethodType:
                obj = obj()        
            data = StringIO.StringIO(obj.data)
            size = (obj.width, obj.height)    
            self._image = PIL.Image.open(PIL.ImageFileIO.ImageFileIO(data))
        else:
            raise RMLPluginError, 'Image %s could not be found' % fileName

    def _jpeg_fh(self):
        fp = self.fp
        fp.seek(0)
        return fp

    def jpeg_fh(self):
        return None

    def getSize(self):
        if (self._width is None or self._height is None):
            self._width, self._height = self._image.size
        return (self._width, self._height)

    def getRGBData(self):
        "Return byte array of RGB data as string"
        if self._data is None:
            im = self._image
            mode = self.mode = im.mode
            if mode not in ('L','RGB','CMYK'):
                im = im.convert('RGB')
                self.mode = 'RGB'
            self._data = im.tostring()
        return self._data

def _image(self, node):
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

