"""
Todd Page
10/8/2011

A few simple tabletop-esque commands
"""

## standard libraries
import random

## custom libraries
from base import PybotPlugin

def pybot_start(pybot):
    tt = Tabletop(pybot)
    return tt

class Tabletop(PybotPlugin):
    def main(self, arguments_lst):
        cmd = arguments_lst[0]
        args = arguments_lst[1:]
        
        if cmd == "die":
            roller_dbref = args[0]
            num = int(args[1])
            sided = int(args[2])
            self.doRollDie(roller_dbref, num, sided)
            
    def doRollDie(self, dbref, num, sided):
        request_lst = [(dbref, "name", "name({0})"),
                       (dbref, "room", "room({0})")]

        data_dct = self.getMUSHAttr(request_lst)
        
        mush = self.buildDataCollection(data_dct,
                                        {"roller": dbref})
        
        result = sum([random.randint(1, sided) for i in range(num)])
        room = mush.roller.room
        name = mush.roller.name
        
        msg = "PyBot: %(name)s rolled %(num)sd%(sided)s -> %(result)s" % locals()
        self.mushRemit(room, msg)
