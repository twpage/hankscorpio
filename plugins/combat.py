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
            
    def doAttack(self, attacker_dbref, defender_name, attack_name):
        loc_defender = self.getLocateResponse(attacker_dbref, defender_name)
        if not loc_defender.isSuccess():
            self.mushPemit(attacker_dbref, loc_defender.getErrorMessage())
            return
        
        defender_dbref = loc_defender.getDBref()
        
        data_dct = self.getMUSHAttr([(attacker_dbref, "name", "name({0})"),
                                     (attacker_dbref, "room", "loc({0})"),
                                     (attacker_dbref, "mode", stat_curmode()),
                                     (attacker_dbref, "possessive", "poss({0})"),
                                     (defender_dbref, "name", "name({0})"),
                                     (defender_dbref, "mode", stat_curmode())])
        
        mush = self.buildDataCollection(data_dct, 
                                        {"attacker": attacker_dbref,
                                         "defender": defender_dbref})

        attack_num = self.getAttackNumberFromName(attacker_dbref, mush.attacker.mode, attack_name)
        full_attack_name = self.getCombatStatAttack(attacker_dbref, mush.attacker.mode, attack_num, "name")
        msg = str.format("Pybot: {0} attacks {1} with {2} {3}.",
                         mush.attacker.name,
                         mush.defender.name,
                         mush.attacker.possessive,
                         full_attack_name)
        
        self.mushRemit(mush.attacker.room, msg)

    def getLocateResponse(self, looker_dbref, name):
        """
        Performs a locate() to return the DBref# associated with a given name
        """
        code = str.format("locate2({0}, {1})", looker_dbref, name)
        dbref = self.getMUSHFunc(code)
        loc = LocateResponse(name, dbref)
        
        return loc
        
    def getCombatStatCore(self, target_dbref, stat_name, schema="CURRENT"):
        mush_code = str.format("u(#8041/fn.get-core-stat, {0}, {1}, {2})",
                               target_dbref,
                               schema,
                               stat_name)
        
        return self.getMUSHFunc(mush_code)
    
    def getCombatStatMode(self, target_dbref, mode_num, stat_name, schema="CURRENT"):
        mush_code = str.format("u(#8041/fn.get-mode-stat, {0}, {1}, {2}, {3})",
                               target_dbref,
                               schema,
                               mode_num,
                               stat_name)
        
        return self.getMUSHFunc(mush_code)
    
    def getCombatStatAttack(self, target_dbref, mode_num, attack_num, stat_name, schema="CURRENT"):
        mush_code = str.format("u(#8041/fn.get-attack-stat, {0}, {1}, {2}, {3}, {4})",
                               target_dbref,
                               schema,
                               mode_num,
                               attack_num,
                               stat_name)
        
        return self.getMUSHFunc(mush_code)
    
    def getAttackNumbers(self, target_dbref, mode_num, schema="CURRENT"):
        mush_code = str.format("lattrp({0}/STATS`{1}`MODE{2}`ATTACK*)",
                               target_dbref,
                               schema,
                               mode_num)
        
        result = self.getMUSHFunc(mush_code)
        attack_attrib_lst = result.split(" ")
        attack_num_lst = []
        for attack_attrib in attack_attrib_lst:
            statsmarker, schema, mode, attack = attack_attrib.split("`")
            attack_num = attack[6:]
            attack_num_lst.append(attack_num)
            
        return attack_num_lst
    
    def getAttackNumberFromName(self, target_dbref, mode_num, attack_name, schema="CURRENT"):
        for attack_num in self.getAttackNumbers(target_dbref, mode_num, schema):
            this_name = self.getCombatStatAttack(target_dbref, mode_num, attack_num, "name")
            if this_name.lower().startswith(attack_name.lower()):
                return attack_num
            
        return None
        
def stat_curmode():
    return "u(#8041/curmode, {0})"

class LocateResponse:
    MATCH_ERROR_NOT_FOUND = -1
    MATCH_ERROR_MULTIPLE = -2
    
    def __init__(self, lookup_text, locate_dbref):
        self.lookup_text = lookup_text
        
        if locate_dbref == "#-1":
            self.success = False
            self.dbref = None
            self.error_type = self.MATCH_ERROR_NOT_FOUND
            
        elif locate_dbref == "#-2":
            self.success = False
            self.dbref = None
            self.error_type = self.MATCH_ERROR_MULTIPLE
        
        else:
            self.success = True
            self.dbref = locate_dbref
            self.error_type = 0
        
    def isSuccess(self):
        return self.success
    
    def getDBref(self):
        return self.dbref if self.isSuccess() else None

    def getErrorMessage(self):
        error_msg = ""
        if self.error_type == self.MATCH_ERROR_NOT_FOUND:
            error_msg = str.format("Could not find a target named '{0}'.", self.lookup_text)
        elif self.error_type == self.MATCH_ERROR_MULTIPLE:
            error_msg = str.format("Multiple targets named '{0}'.", self.lookup_text)
        return error_msg
    