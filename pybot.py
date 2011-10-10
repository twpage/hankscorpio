"""
Todd Page
10/8/2011

Telnet Interface between PennMUSH and Python
"""

import telnetlib, ConfigParser, time, os, imp, random

class Pybot:
    def __init__(self, host, port, player, password):
        self.host = host
        self.port = port
        self.player = player
        self.password = password
        self.secret_code = None
        
        ## Modules
        self.modules_dir = os.path.join(os.getcwd(), "plugins")
        self.plugin_scan_dct = {}
        self.plugin_dct = {}
        self.scanModules()
        
        ## telnet vars
        self.ShouldQuit = False
        self.telnet = None
        
    def run(self):
        tn = telnetlib.Telnet(self.host, self.port)
        self.telnet = tn
        
        self.sendToTelnet(str.format("ch \"{0}\" {1}", self.player, self.password))
        self.sendToTelnet("p hazard=I connected at [time()]")
        self.echo("pybot has connected")
        
        self.secret_code = "PYBOT" + str(random.randint(1, 9999999))
        self.sendToTelnet(str.format("&PYBOT_CODE me={0}", self.secret_code))
        
        self.listen()
        self.telnet.close()

    def sendToTelnet(self, socket_msg):
        self.telnet.write(socket_msg+"\n")
    
    def listen(self):
        while not self.ShouldQuit:		
            text = self.telnet.read_until("\n")
            text = text.strip()
            print "%s" % text
            if text.startswith(self.secret_code):
                command_lst = text.split(":")
                cmd = command_lst[1]
                args_lst = command_lst[2:]
                self.processCommand(cmd, *args_lst)

    def echo(self, text):
        print str.format("->{0}", text)
        
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
            
        ## otherwise, try to execute code from a plugin
        elif cmd_name in self.plugin_dct.keys():
            self.plugin_dct[cmd_name].main(args)

        return

    def scanModules(self):
        for filename in os.listdir(self.modules_dir):
            if not filename.endswith(".py"): continue
            #if filename == "base.py": continue
            
            mod_name, ext = os.path.splitext(filename)
            mod_file = os.path.join(self.modules_dir, filename)
            
            modified = os.stat(mod_file).st_mtime
            
            stored_modified = self.plugin_scan_dct.get(filename, 0)
            
            if modified > stored_modified:
                self.echo(str.format("importing module {0}", filename))
                module = imp.load_source(mod_name, mod_file)
                plugin = module.pybot_start(self)
                self.plugin_scan_dct[filename] = modified
                self.plugin_dct[mod_name] = plugin
                
    def getFromMUSH(self, mush_text):
        """
        Get any generic data from the MUSH
        
        Sends any given text to the MUSH and WAITS on the 
        telnet response
        """
        self.sendToTelnet(mush_text)
        resp_text = self.telnet.read_until("\n")
        resp_text = resp_text.strip() ## clear off weird whitespace
        self.echo(resp_text)
        
        return resp_text
    
    def getBulkDataFromMUSH(self, request_lst):
        """
        Get a bunch of attribute data from the MUSH at once
        
        Given a list of 2-tuples (dbref, attr),
        return a data dictionary of (dbref, attr) -> value from MUSH
        
        By default, performs a simple [get(dbref/attr)] lookup on the MUSH
        Optionally, pass in 3-tuple (dbref, attr, code) code will pass dbref in as {0}
        """
        ## construct a request string for Pybot to read
        request_token_lst = []
        for request_tpl in request_lst:
            dbref = request_tpl[0]
            attr = request_tpl[1]
            
            if len(request_tpl) == 3:
                mush_code = "[" + str.format(request_tpl[2], dbref) + "]"
            else:
                mush_code = str.format("[get({0}/{1}]", dbref, attr)
                
            req_token = str.format("{0}^{1}^{2}", dbref, attr, mush_code)
            request_token_lst.append(req_token)
            
        mush_request_text = "th " + ":".join(request_token_lst)
        
        ## send this request to the MUSH ('think' the results)
        mush_response_text = self.getFromMUSH(mush_request_text)
        
        ## parse the results into a usable data dictionary
        data_dct = {}
        
        for resp_token in mush_response_text.split(":"):
            dbref, attribute, value = resp_token.split("^")
            data_dct[(dbref, attribute)] = value
        
        return data_dct

def main():
    config = ConfigParser.ConfigParser()
    config.optionxform = str
    config.read("tf2005.cfg")
    
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
    
