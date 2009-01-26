"""
Re-imagined DeviceAtlas API:

>>> from deviceatlas import DeviceAtlas
>>> DA = DeviceAtlas('/Users/johnboxall/git/device/DeviceAtlas.json')
>>> ua = 'Mozilla/5.0 (SymbianOS/9.2; U; Series60/3.1 NokiaN95/11.0.026; Profile MIDP-2.0 Configuration/CLDC-1.1) AppleWebKit/413 (KHTML, like Gecko) Safari/413'
>>> n95 = DA.device(ua)
>>> n95.model
'N95'

"""
import simplejson


# Mapping from DA property types to Python types.
PROPERTY_MAP = dict(s=str, b=bool, i=int, d=str)


class Device(dict):
    """
    Thin wrapper `dict` that allows keys to be accessed like attributes.
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
        Loads and initializes DA JSON from `jsonpath`.
        
        """
        self.data = simplejson.load(open(jsonpath, 'r'))        
        # Turn the Device Atlas properties into a dictionary:
        # {<da_property_id>: (<property_name>, <python_type_function>), ... }
        self.data['properties'] = {}
        for index, value in enumerate(self.data['p']):
            property_index = str(index)  # DA properties are typed as strs
            property_name = value[1:]
            property_type = PROPERTY_MAP[value[0]]
            self.data['properties'][property_index] = (property_name, property_type)
        # Change all lists in data to dicts.
        self.data = list2dict(self.data)

    def device(self, ua):
        """
        Returns a `Device` for a User-Agent string `ua`.
        
        """
        return Device(self._getProperties(ua.strip()))

    def _getProperties(self, ua):
        """
        Returns a `dict` of device properties given a User-Agent string `ua`.

        """
        idProperties = {}
        matched = ''
        sought = None
        sought, matched = self._seekProperties(ua, idProperties, sought, matched)
        properties = {}
        for index, value in idProperties.iteritems():
            properties[self.data['properties'][index][0]] = self.data['properties'][index][1](value)
        properties['_matched'] = matched
        properties['_unmatched'] = ua[len(matched):]
        return properties

    def _seekProperties(self, unmatched, properties, sought, matched, node=None):
        """
        Seek properties for a UA within `node` starting at the top of the tree.
                
        """
        if node is None:
            node = self.data['t']
        
        if 'd' in node:
            if sought is not None and len(sought) == 0:
                return sought, matched
            for property, value in node['d'].iteritems():
                if sought is None or property in sought:
                    properties[property] = value
                if sought is not None and \
                   (('m' not in node) or ('m' in node and property not in node['m'])):
                    if property in sought:
                        del sought[property]
                        
        if 'c' in node:
            for c in range(1, len(unmatched)+1):
                seek = unmatched[0:c]
                if seek in node['c']:
                    matched += seek
                    sought, matched = self._seekProperties(unmatched[c:], properties, sought, matched, node['c'][seek])
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