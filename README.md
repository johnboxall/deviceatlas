Unofficial Python Device Atlas API
=================================

About
-----

_Device Atlas:http://deviceatlas.com/ is a database of mobile device information. The official is available at http://deviceatlas.com/downloads. This API is just a bit more awesome.

**Official API:**

    >>> import api
    >>> DA = api.DaApi()
    >>> tree = DA.getTreeFromFile('DeviceAtlas.json')
    >>> DA.getTreeRevision(tree)
    >>> ua = 'SonyEricssonW850i/R1GB Browser/NetFront/3.3 Profile/MIDP-2.0 Configuration/CLDC-1.1'
    >>> DA.getProperties(tree, ua)
    {u'gprs': '1', u'mpeg4': '1', u'drmOmaForwardLock': '1', ...
    
**Awesome API:**

    >>> from deviceatlas import DeviceAtlas
    >>> DA = DeviceAtlas(''DeviceAtlas.json')
    >>> ua = 'SonyEricssonW850i/R1GB Browser/NetFront/3.3 Profile/MIDP-2.0 Configuration/CLDC-1.1'
    >>> DA.device(ua)
    {u'gprs': '1', u'mpeg4': '1', u'drmOmaForwardLock': '1', ...