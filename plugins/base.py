"""
Todd Page
10/8/2011

Base Plugin, others should import from this
"""
## standard libraries

## custom libraries


def pybot_start(pybot):
    return None

class PybotPlugin:
    def __init__(self, pybot):
        self.pybot = pybot
        
    def launch(self):
        raise NotImplementedError("launch method is missing from this plugin")
    
    def sendToMUSH(self, msg):
        self.pybot.sendToTelnet(msg)
        
    def callback(self, callback_fn, *args):
        self.pybot.startPluginDataCallback(callback_fn, args)
        
    def mushRemit(self, room_dbref, msg):
        self.sendToMUSH("th [remit(%(room_dbref)s, %(msg)s)]" % locals())
        
    def mushPemit(self, dbref, msg):
        self.sendToMUSH("th [pemit(%(dbref)s, %(msg)s)]" % locals())

    def buildDataCollection(self, response_data_dct, name_to_dbref_dct):
        collection = DataCollection()
        for name, dbref in name_to_dbref_dct.items():
            collection.addObject(dbref, name)
            
        for (dbref, attrib), value in response_data_dct.items():
            obj = collection.getObjectByDBref(dbref)
            obj.addAttribute(attrib, value)
            
        return collection
    
    def getFromMUSH(self, mush_text):
        return self.pybot.getFromMUSH(mush_text)
    
    def getMUSHFunc(self, mush_text):
        return self.pybot.getFromMUSH("th [" + mush_text + "]")
    
    def getMUSHAttr(self, pairs_lst):
        """
        Given list of 2-tuple (dbref, attrib) pairs, return value dictionary as string
        """
        attr_data_dct = self.pybot.
        
    
class DataCollection:
    def __init__(self):
        self.dbref_dct = {}
        
    def addObject(self, dbref, name):
        setattr(self, name, DataCollectionObject())
        self.dbref_dct[dbref] = name
        
    def getObjectByDBref(self, dbref):
        return getattr(self, self.dbref_dct[dbref])
    
class DataCollectionObject:
    def addAttribute(self, attrib, value):
        setattr(self, attrib, value)
        
