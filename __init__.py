def initialize(context):
    # Import lazily, and defer initialization to the module
    import XMLTemplate, XSLTTemplate, DTCacheManager
    XMLTemplate.initialize(context)
    XSLTTemplate.initialize(context)
    DTCacheManager.initialize(context)

# do a quick import of the plugins, in order to get any errors immediately
import plugins
