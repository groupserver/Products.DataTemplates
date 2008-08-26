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
import os, Globals

from Products.PageTemplates import PageTemplateFile
from BTrees.OOBTree import OOBTree
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager

class DTCacheManagerAware:
    """ A Mixin proxy class for locating and using a DTCacheManager instance.
    
    """
    null_cache_manager = 'no cache manager'
    def get_cacheManagerIds(self, addnull=1):
        """ Find all the cache managers in our aquisition path.

        """
        if addnull:
            cache_managers = [self.null_cache_manager]
        else:
            cache_managers = []
        
        current = self
        while current:
            if getattr(current, 'isPrincipiaFolderish', None):
                for cache_manager in current.objectValues('DT Cache Manager'):
                    cache_manager_id = cache_manager.getId()
                    if cache_manager_id not in cache_managers:
                        cache_managers.append(cache_manager_id)
            try:
                current = current.aq_parent
            except:
                break

        return cache_managers

    def get_cacheManagerIdsNoNull(self):
        """ Get the cache manager ids without the null value.

        A helper method because we can't pass parameters in the _properties
        select_variable.

        """
        return self.get_cacheManagerIds(0)

    def get_cacheManager(self):
        """ Get the currently selected cache manager.
        
        """
        cache_manager_id = getattr(self, 'cache_manager',
                                   self.null_cache_manager)
        if cache_manager_id != self.null_cache_manager:
            return getattr(self, cache_manager_id, None)
        self.cache_manager = ''
        
        return None
    
    def prune_cache(self):
        """ Prune the currently selected cache.

        """
        cache_manager = self.get_cacheManager()
        if cache_manager:
            cache_manager.prune_cache()
            
    def invalidate_cache(self):
        """ Invalidate all the cache managers in our aquisition path.

        Note: We actually only invalidate the cache manager _closest_ to
        us if there is more than one with the same ID in our acquisition
        path, on the assumption that if someone has created two cache managers
        with the same ID, they probably intend one of them to override the
        other.
        
        """
        cache_manager_ids = self.get_cacheManagerIds()
        for cache_manager_id in cache_manager_ids:
            cache_manager = getattr(self, cache_manager_id, None)
            if cache_manager:
                cache_manager.invalidate_cache()

    def retrieve_cache(self, xslt_obj, source):
        """ Retrieve a page from the currently selected cache.
        
        """
        cache_manager = self.get_cacheManager()
        if cache_manager:
            cached = cache_manager.retrieve_cache(xslt_obj, source)
        else:
            cached = None

        return cached

    def update_cache(self, xslt_obj, source, result, anonymous_only=1):
        """ Update a page in the currently selected cache.
        
        """
        cache_manager = self.get_cacheManager()
        if cache_manager:
            cache_manager.update_cache(xslt_obj, source, result,
                                       anonymous_only)
    
class DTCacheManager(SimpleItem, PropertyManager):
    """ A Cache manager for DataTemplates.

    """
    security = ClassSecurityInfo()
    
    meta_type = "DT Cache Manager"
    
    version = 1.11
    
    manage_options = PropertyManager.manage_options + SimpleItem.manage_options
    
    anonymous_expiry_time = 86400 # 1 day
    authenticated_expiry_time = 7200 # 2 hours
    prune_interval = 600 # 10 mins
    cache_dir = os.path.join(Globals.package_home(globals()), 'cache')
    _def_properties=({'id':'anonymous_expiry_time', 'type': 'int', 'mode': 'w'},
                     {'id':'authenticated_expiry_time', 'type': 'int', 'mode': 'w'},
                     {'id':'prune_interval', 'type': 'int', 'mode': 'w'},
                     {'id':'cache_dir', 'type': 'string', 'mode': 'w'},
                     )
    _properties = _def_properties

    def __init__(self, id):
        """ Initialise an instance of DTCacheManager.

        """
        self.id = id

    security.declareProtected('Manage properties', 'upgrade')
    def upgrade(self):
        """ Upgrade to the latest version.

        """
        currversion = getattr(self, '_version', 0)
        if currversion == self.version:
            return 'already running latest version (%s)' % currversion
        
        self._properties = self._def_properties
        self._version = self.version

        return 'upgraded %s to version %s from version %s' % (self.getId(),
                                                              self._version,
                                                              currversion)     
    security.declarePrivate('retrieve_cache')
    def retrieve_cache(self, xslt_obj, source):
        """ Retrieve from the page cache.
        
        """
        import md5, time
        
        if self.version > getattr(self, '_version', 0):
            self._invalidate_cache()
            
        checksum = md5.new(source).hexdigest()
        
        page_cache = getattr(self, '_page_cache', OOBTree())
        
        result = page_cache.get('%s%s' %(xslt_obj.getId(), checksum), None)
        
        if not result:
            # Cache miss
            return None
        
        if result[2] == 0:
            cet = self.anonymous_expiry_time
        else:
            cet = self.authenticated_expiry_time
            
        if time.time() - result[1] > cet:
            self.prune_cache()
            return None
        
        try:
            cache_file = file('%s/%s' % (self.cache_dir, result[0]))
        except (IOError, OSError):
            # we should rightfully panic here :)
            self.invalidate_cache()
            return None
        
        # cache hit
        return cache_file.read()
    
    security.declareProtected('Manage properties', 'prune_cache')
    def prune_cache(self, force=0, flush=0):
        """ Prune the cache back so we don't have stale records.
        
        """
        import time
        
        version = getattr(self, '_version', 0)
        if version < self.version:
            return self.invalidate_cache()
        
        if (not force) and (not (time.time() - getattr(self,
                                                       '_last_pruned',
                                                       0)) >
                      self.prune_interval):
            return 0
        
        page_cache = getattr(self, '_page_cache', OOBTree())
        delukeys = []
        for ukey in page_cache.keys():
            if page_cache[ukey][2] == 0:
                cet = self.anonymous_expiry_time
            else:
                cet = self.authenticated_expiry_time
                
            if flush or (time.time() - page_cache[ukey][1]) > cet:
                try:
                    os.remove('%s/%s' % (self.cache_dir,
                                         page_cache[ukey][0]))
                except (IOError, OSError):
                    pass
                
                delukeys.append(ukey)

        for ukey in delukeys:
            del(page_cache[ukey])
            
        self._page_cache = page_cache
        
        self._last_pruned = time.time()
        
        return 1
        
    security.declarePrivate('update_cache')
    def update_cache(self, xslt_obj, source, result, anonymous_only=1):
        """ Update the page cache, based on several conditions.
        
        """
        import time, md5, AccessControl
        
        sm = AccessControl.getSecurityManager()
        user_id = sm.getUser().getId()
        if anonymous_only and user_id != None:
            return 0
        
        checksum = md5.new(source).hexdigest()
        
        page_cache = getattr(self, '_page_cache', OOBTree())
        
        # create the cache file name -- include the user_id, primarily for
        # debugging
        xid = xslt_obj.getId()
        cache_fname = '%s_%s_%s' % (xid, user_id, checksum)
        cachekey = '%s%s' % (xid, checksum)
        if user_id == None:
            page_cache[cachekey] = (cache_fname, time.time(), 0)
        else:
            page_cache[cachekey] = (cache_fname, time.time(), 1)

        cache_file = file('%s/%s' % (self.cache_dir, cache_fname), 'w+')
        cache_file.write(result)
        cache_file.close()
        
        self._page_cache = page_cache
        
        return 1
    
    security.declarePrivate('invalidate_cache')
    def invalidate_cache(self):
        """ Invalidate the page cache.
        
        """
        version = getattr(self, '_version', 0)
        if not (version < self.version):
            # if we're upgrading the cache, don't prune the cache
            self.prune_cache(1, 1)

        self._page_cache = OOBTree()
        self._last_pruned = 0
        self._version = self.version
        
        return 1

#
# Zope Management Methods
#
def manage_addDTCacheManager(self, id,
                             REQUEST=None, RESPONSE=None, submit=None):
    """ Add a new instance of DTCacheManager.

    """
    obj = DTCacheManager(id)
    self._setObject(id, obj)
    obj = getattr(self, id)
    if RESPONSE and submit:
        RESPONSE.redirect('/%s/manage_workspace' % obj.absolute_url(1))

manage_addDTCacheManagerForm = PageTemplateFile.PageTemplateFile(
    'management/manage_addDTCacheManagerForm.zpt',
    globals(), __name__='manage_addDTCacheManagerForm')

def initialize(context):
    context.registerClass(
        DTCacheManager,
        permission='Add DT Cache Manager',
        constructors=(manage_addDTCacheManagerForm,
                      manage_addDTCacheManager),
        icon='icons/cache.gif'
        )
