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
    sys.stderr.write('Problem importing DataTemplate RML plugin %s\n' % plugin_name)
    traceback.print_exc(sys.stderr)

plugin_registry = {}

try:
    import plugin_trml2pdf
    plugin_trml2pdf.register_plugin(plugin_registry)
except:
    log_tb('plugin_trml2pdf')
