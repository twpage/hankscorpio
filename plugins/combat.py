"""
Todd Page
10/9/2011

Simple combat functions
"""

## standard libraries
import random

## custom libraries
from base import PybotPlugin

def pybot_start(pybot):
    c = Combat(pybot)
    return c

class Combat(PybotPlugin):
    def main(self, arguments_lst):
        cmd = arguments_lst[0]
        args = arguments_lst[1:]
        
        ## cmd: attack
        ## args: attacker, defender, attack name, dmg level
        if cmd == "attack":
            self.doAttack(*args)
            
    def locate(self, looker_dbref, name):
        """
        Performs a locate() to return the DBref# associated with a given name
        """
        code = str.format("locate2({0}, {1})", looker_dbref, name)
        dbref = self.getMUSHFunc(code)
        
        return dbref
        
    def doAttack(self, attacker_dbref, defender_name, attack_name):
        defender_dbref = self.getMUSHFuncFmt("pmatch(*{0})", defender_name)
        
        data_dct = self.getMUSHAttr([(attacker_dbref, "name", "name({0})"),
                                     (attacker_dbref, "room", "loc({0})"),
                                     (attacker_dbref, "possessive", "poss({0})"),
                                     (defender_dbref, "name", "name({0})")])
        
        mush = self.buildDataCollection(data_dct, 
                                        {"attacker": attacker_dbref,
                                         "defender": defender_dbref})
                                     
        msg = str.format("Pybot: {0} attacks {1} with {2} {3}.",
                         mush.attacker.name,
                         mush.defender.name,
                         mush.attacker.possessive,
                         attack_name)
        
        self.mushRemit(mush.attacker.room, msg)
