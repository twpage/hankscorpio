"""
Todd Page
10/8/2011

Telnet Interface between PennMUSH and Python
"""

import telnetlib, ConfigParser, time, os, imp
CONST_PYBOT_CODE = "PYBOT5731"
class Pybot:
    def __init__(self, host, port, player, password):
        self.host = host
        self.port = port
        self.player = player
        self.password = password
        
        ## Modules
        self.modules_dir = os.path.join(os.getcwd(), "plugins")
        self.plugin_scan_dct = {}
        self.plugin_dct = {}
        self.scanModules()
        
        ## callbacks
        self.callback_key = 0
        self.callback_dct = {}
        
        ## telnet vars
        self.ShouldQuit = False
        self.telnet = None
        
    def run(self):
        tn = telnetlib.Telnet(self.host, self.port)
        self.telnet = tn
        
        self.sendToTelnet("ch \"%s\" %s" % (self.player, self.password))
        self.sendToTelnet("p hazard=I connected at [time()]")
        print "pybot has connected"
        
        self.listen()
        self.telnet.close()

    def sendToTelnet(self, socket_msg):
        self.telnet.write(socket_msg+"\n")
    
    def listen(self):
        while not self.ShouldQuit:		
            text = self.telnet.read_until("\n")
            text = text.strip()
            print "%s" % text
            if text.startswith(CONST_PYBOT_CODE):
                command_lst = text.split(":")
                cmd = command_lst[1]
                args_lst = command_lst[2:]
                self.processCommand(cmd, *args_lst)

    def processCommand(self, cmd_name, *args):
        #print "-> got command |%s|" % cmd_name
        if cmd_name == "quit":
            #print "bye!"
            self.ShouldQuit = True

        elif cmd_name == "look":
            self.sendToTelnet("look")

        elif cmd_name == "pose":
            pose_cmd = ":" + args[0] + "\n"
            self.sendToTelnet(pose_cmd)

        elif cmd_name == "say":
            pose_cmd = "\"" + args[0] + "\n"
            self.sendToTelnet(pose_cmd)

        elif cmd_name == "walk":
            walk_cmd = "go " + args[0] + "\n"
            self.sendToTelnet(walk_cmd)

        elif cmd_name == "scan":
            self.scanModules()
            
        elif cmd_name == "bulkattr":
            ## xxxxx:bulkattr:TOKEN1:TOKEN2:TOKEN3
            ## where TOKEN = DBREF^ATTR^VALUE
            callback_key = args[0]
            tokens = args[1:]
            self.handleBulkAttributeResponse(callback_key, tokens)
            
        ## otherwise, try to execute code from a plugin
        elif cmd_name in self.plugin_dct.keys():
            self.plugin_dct[cmd_name].main(args)

        return

    def handleBulkAttributeResponse(self, callback_key, attr_token_lst):
        """
        Receives a list of MUSH tokens like DBREF^ATTR^VALUE
        and loads them into the local attribute database
        """
        data_dct = {}
        for token in attr_token_lst:
            dbref, attribute, value = token.split("^")
            data_dct[(dbref, attribute)] = value
        
        if callback_key in self.callback_dct:
            self.doPluginDataCallback(callback_key, data_dct)
            
        return True
            
    def sendBulkAttributeRequest(self, callback_key, request_lst):
        """
        Send a pair of 3-tuples (dbref, attribute, <optional request code>)
        """
        mush_text_lst = []
        for (dbref, attribute, req_code) in request_lst:
            mush_text = "%(dbref)s^%(attribute)s^" % locals()
            if req_code:
                req_code = req_code.replace("#", dbref)
                mush_text += "[%(req_code)s]" % locals()
            else:
                mush_text += "[get(%(dbref)s/%(attribute)s)]" % locals()
                
            mush_text_lst.append(mush_text)
            
        bulk_attr_text = str.format("th {0}:bulkattr:{1}:{2}",
                                    CONST_PYBOT_CODE,
                                    str(callback_key),
                                    ":".join(mush_text_lst))
        #bulk_attr_text = "th PYBOT5731:bulkattr:" + str(callback_key) + ":" + ":".join(mush_text_lst)
        self.sendToTelnet(bulk_attr_text)
        
    def scanModules(self):
        for filename in os.listdir(self.modules_dir):
            if not filename.endswith(".py"): continue
            #if filename == "base.py": continue
            
            mod_name, ext = os.path.splitext(filename)
            mod_file = os.path.join(self.modules_dir, filename)
            
            modified = os.stat(mod_file).st_mtime
            
            stored_modified = self.plugin_scan_dct.get(filename, 0)
            
            if modified > stored_modified:
                print "importing module %s" % filename
                module = imp.load_source(mod_name, mod_file)
                plugin = module.pybot_start(self)
                self.plugin_scan_dct[filename] = modified
                self.plugin_dct[mod_name] = plugin
                
    def startPluginDataCallback(self, callback_fn, args):
        request_lst = callback_fn(*args, DataRequest={}) ## function should return list
        
        ## TODO: probably a better way to make keys
        self.callback_key += 1
        
        callback_key = str(self.callback_key)
        self.callback_dct[callback_key] = (callback_fn, args)
        
        self.sendBulkAttributeRequest(callback_key, request_lst)
        
    def doPluginDataCallback(self, callback_key, data_dct):
        callback_fn = self.callback_dct[callback_key][0]
        callback_args = self.callback_dct[callback_key][1]
        del self.callback_dct[callback_key]
        
        callback_fn(*callback_args, DataRequest=data_dct)
        
    def getFromMUSH(self, mush_text):
        self.sendToTelnet(mush_text)
        text = self.telnet.read_until("\n")
        text = text.strip()
        print "%s" % text
        return text
    

def main():
    config = ConfigParser.ConfigParser()
    config.optionxform = str
    config.read("pybot.cfg")
    
    pybot = initPybotFromConfigFile(config)
    pybot.run()
    
def initPybotFromConfigFile(config):
    assert isinstance(config, ConfigParser.ConfigParser)
    
    pybot = Pybot(host=config.get("general", "host"),
                  port=config.get("general", "port"),
                  player=config.get("general", "player"),
                  password=config.get("general", "password"))
    
    return pybot
    
class AttributeStorageError(Exception):
    pass

if __name__ == '__main__':
    main()
    
