"""
Revised DeviceAtlas API:

>>> from deviceatlas import DeviceAtlas
>>> DA = DeviceAtlas('/Users/johnboxall/git/device/DeviceAtlas.json')
>>> ua = 'Mozilla/5.0 (SymbianOS/9.2; U; Series60/3.1 NokiaN95/11.0.026; Profile MIDP-2.0 Configuration/CLDC-1.1) AppleWebKit/413 (KHTML, like Gecko) Safari/413'
>>> n95 = DA.device(ua)
>>> n95.model
'N95'
>>> 

"""
import simplejson


# Mapping from DA property types to Python types.
PROPERTY_MAP = dict(s=str, b=bool, i=int, d=str)


class Device(dict):
    """
    Thin wrapper around a `dict` that allows keys to be accessed like attributes.
    Returns `None` if the accessed attribute does not exist.
    
    """
    def __init__(self, data):
       super(Device, self).__init__(data)
        
    def __getattr__(self, name):
        try:
            return self[name]
        except IndexError:
            return None


class DeviceAtlas(object):
    def __init__(self, jsonpath):
        """
        Open `jsonpath` and loader in.
        """
        self.data = simplejson.load(open(jsonpath, 'r'))        
        # Turn the Device Atlas properties into a dictionary:
        # {<da_property_id>: (<property_name>, <python_type_function>), ... }
        self.data['properties'] = {}
        for index, value in enumerate(self.data['p']):
            property_index = str(index)
            property_name = value[1:]
            property_type = PROPERTY_MAP[value[0]]
            self.data['properties'][property_index] = (property_name, property_type)
        # Change all lists in data to dicts.
        self.data = list2dict(self.data)

    def device(self, ua):
        """
        Given a User-Agent string return a `Device` for that UA.
        
        """
        return Device(self._getProperties(ua.strip()))

    def _getProperties(self, ua):
        """
        Given a User-Agent string return a `dict` of all known properties.

        """
        idProperties = {}
        matched = ''
        sought = None
        sought, matched = self._seekProperties(self.data['t'], ua, idProperties, sought, matched)
        properties = {}
        for index, value in idProperties.iteritems():
            properties[self.data['properties'][index][0]] = self.data['properties'][index][1](value)
        properties['_matched'] = matched
        properties['_unmatched'] = ua[len(matched):]
        return properties

    def _seekProperties(self, node, string, properties, sought, matched):
        """
        Seek properties for a UA within a node
        This is designed to be recursed, and only externally called with the
        node representing the top of the tree

        `node` is array
        `string` is string
        `properties` is properties found
        `sought` is properties being sought
        `matched` is part of UA that has been matched
        
        """        
        unmatched = string
        
        if 'd' in node:
            if sought != None and len(sought) == 0:
                return sought, matched
            for property, value in node['d'].iteritems():
                if sought == None or sought.has_key(property):
                    properties[property] = value
                if (sought != None and 
                    ( (not node.has_key('m')) or (node.has_key('m') and (not node['m'].has_key(property)) ) ) ):
                    if sought.has_key(property):
                        del sought[property]

        if 'c' in node:
            for c in range(1, len(string)+1):
                seek = string[0:c]
                if seek in node['c']:
                    matched += seek
                    sought, matched = self._seekProperties(node['c'][seek], string[c:], properties, sought, matched)
                    break
            
        return sought, matched


def list2dict(tree):
    """
    Recursively changes lists in passed tree to dictionaries with
    string index keys.
    
    """
    if isinstance(tree, dict):
        # `tree` is a dict - convert any list items into dictionaries.
        for key, item in tree.iteritems():
            if isinstance(item, dict) or isinstance(item, list):
                tree[key] = list2dict(item)
    elif isinstance(tree, list):
        # `tree` is a list - convert it to a dictionary.
        tree = dict((str(i), item) for i, item in enumerate(tree))
        tree = list2dict(tree)
    return tree