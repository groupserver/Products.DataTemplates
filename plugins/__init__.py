import plugin_4suite, plugin_libxslt

plugin_registry = {}

plugin_4suite.register_plugin(plugin_registry)
plugin_libxslt.register_plugin(plugin_registry)

#plugin_registry = {'http://iopen.co.nz/plugins/xslt/4suite': ('4Suite',
#                                                              plugin_4suite),
#                   'http://iopen.co.nz/plugins/xslt/libxslt': ('libxslt',
#                                                               plugin_libxslt)}
