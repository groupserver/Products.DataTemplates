# Copyright IOPEN Technologies Ltd., 2003
# richard@iopen.net
#
# For details of the license, please see LICENSE.
#
# You MUST follow the rules in README_STYLE before checking in code
# to the head. Code which does not follow the rules will be rejected.  
#
import sys, traceback
def log_tb(plugin_name):
    sys.stderr.write('Problem importing DataTemplate plugin %s\n' % plugin_name)
    traceback.print_exc(sys.stderr)
    

plugin_registry = {}

try:
    import plugin_4suite_1_0a1
    plugin_4suite_1_0a1.register_plugin(plugin_registry)
except:
    log_tb('4suite_1_0a1')
try:
    import plugin_4suite
    plugin_4suite.register_plugin(plugin_registry)
except:
    log_tb('4suite')
try:
    import plugin_libxslt
    plugin_libxslt.register_plugin(plugin_registry)
except:
    log_tb('libxslt')
