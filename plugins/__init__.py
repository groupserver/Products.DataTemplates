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

try:
    import plugin_pyana
    plugin_pyana.register_plugin(plugin_registry)
except:
    log_tb('pyana')
