#!/usr/bin/env python3
import items
import regions
import characters
import enemies
from player import *
from helpers import *
import csv
import sys
import time
import re

def csv_loader(filename, readall=False):
    returnList = []
    with open(filename) as csvfile:
        for row in csv.reader(csvfile):
            returnList.append(row)
    if readall:
        return returnList
    else:
        return returnList[1:]

def load_bar(count, total, bar_length, status="", show_percent=True, show_wall=True, fill="#", space = " ", before="", finished = ""):
    filled_len = int(round(bar_length * count / float(total)))

    bar = fill * filled_len + space * (bar_length - filled_len)

    if show_wall:
        bar = '['+bar+']'

    percent = ''
    if show_percent:
        percent = round(100.0 * count / float(total), 1)
        percent = ' ' + str(percent)+'% '
    
    if(count == total):
        status = finished

    sys.stdout.write('%s%s%s%s\r' % (before,bar,percent,status))
    sys.stdout.flush()

class Game:
    def __init__(self):

        self.functions = {
            "name":self.player_replace,
            "n":self.new_line,
            "s":self.scramble,
            "z":self.set_flag_from_text
        }

        self.flags = {}
        self.load_flags()

        self.item_book = {}
        for item in csv_loader("data/items.csv"):
            self.item_book[item[0]] = getattr(items, item[2])(item[0],item[1],item[3],item[4],self)

        self.region_book = {}
        for region in csv_loader("data/regions.csv"):
            self.region_book[region[0]] = getattr(regions, region[1])(region[0],region[2],self)

        self.character_book = {}
        for character in csv_loader("data/characters.csv"):
            self.character_book[character[0]] = getattr(characters, character[1])(character[0],character[2],character[3],character[4],self)
        
        for enemy in csv_loader("data/enemies.csv"):
            self.character_book[enemy[0]] = getattr(enemies, enemy[1])(enemy[0],enemy[2],enemy[3],enemy[4],enemy[5],enemy[6],self)

        self.player = Player("Dove", list(self.region_book.values())[0], self)

        self.default_commands = {
            'exit':self.exit_game,
            'help':self.display_help,
            'curl':self.player.display_region,
            'nmap':self.display_entities,
            'inventory':self.get_player().display_inv,
            'clear':clearView
        }

        self.help_text = ""
        with open('data/help.txt', 'r') as file:
            self.help_text = file.read()
    
    def start(self):
        clearView()
        self.boot_sequence()
        self.name_sequence()
        self.player.current_location.pre_load()
    
    def boot_sequence(self):
        print("WELCOME TO ///ICENET")
        self.simulate_load(3,3,0.2,'', False, False,'.',' ','Condition ',' STABLE')
        self.simulate_load(10,3,0.05,'', False, False,'.',' ','Checking connection ',' WIRED')
        self.simulate_load(3,3,0.1,'', False, False,'.',' ','Realism ',' OFF')
        self.simulate_load(3,3,0.1,'', False, False,'.',' ','Graphics ',' MINIMAL')
        print("")
        print("####### PRIVILEGES #######")
        print("SEARCHING CITIES ...")
        self.simulate_load(3,3,0.05,'', False, False,'.',' ','matrix.city ',' FAILED')
        self.simulate_load(3,3,0.05,'', False, False,'.',' ','777.city ',' FAILED')
        self.simulate_load(3,3,0.1,'', False, False,'.',' ','star.city ',' FAILED')
        print("Major cities did not catch other .city privleges.")
        print("NO ACCESS")
        print("")
        print("SEARCHING TOWNS...")
        self.simulate_load(3,3,0.05,'', False, False,'.',' ','cozy.town ',' FAILED')
        self.simulate_load(3,3,0.05,'', False, False,'.',' ','anarchist.town ',' FAILED')
        self.simulate_load(20,20,0.05,'', False, False,'.',' ','In depth search ','')
        self.simulate_load(3,3,0.1,'', False, False,'.',' ','lily.town ',' OK!')
        print("DONE!")
        print("")
        print("Connection allowed on domain(s): <lily.town>")
        self.simulate_load(50,50,0.05,"...Connecting to <lily.town>",finished="DONE                                ")
        print("")

    def name_sequence(self):
        print("Verification token [INVALID]")
        print("Please verify this connection with a name!")
        while True:
            try:
                name = str(input('name: ')).strip()
                if len(name) > 12:
                    print("Name too long (over 12 characters). Enter again.")
                elif name in self.default_commands:
                    print("Invalid name.")
                elif (name.replace(' ', '') != ""):
                    self.player.name = name
                    break
                else:
                    break
            except:
                print("Invalid name. Please try again.")
        self.simulate_load(3,3,0.2,'', False, False,'.',' ','Verifying connection ',' OK!')
        print("Name ["+self.player.get_name()+"] is correct. CONNECTION VERIFIED!")
        print("Type [help] for more info.")
        print("Connecting to <connect.lily.town>...")
        time.sleep(1.5)
        print("")

    def simulate_load(self, total, bar_length, sleep_time=0.5, status='', show_percent=True, show_wall=True, fill='#', space = ' ', before='',finished=''):
        for i in range(total+1):
            load_bar(i, total, bar_length, status, show_percent, show_wall, fill, space, before, finished)
            time.sleep(sleep_time)
        print("")

    def update(self):
        command = input("["+str(self.flags['progression'])+" "+self.get_player().get_name()+" <"+self.get_player().get_current_location().name+">]# ").strip()
        if self.execute(command):
            self.update_data()

    def update_data(self):
        self.player.get_current_location().update()
        self.player.update()
        self.region_book['none.lily.town'].update()

    def load_text(self, text):
        keys = set(re.findall("{(.+?)}", text))
        for k in keys:
            if k in self.functions:
                text = self.functions[k](text)
        return text

    def new_line(self, text):
        return text.replace("{n}", "\n")
    
    def player_replace(self, text):
        return text.replace("{name}", self.player.get_name())
    
    def scramble(self, text):
        r = re.findall('\{s\}.*\{\\\s\}', text)
        for s in r:
            text = text.replace(s, ran_string(len(s) - 7))
        return text
    def set_flag_from_text(self, text):
        r = re.findall('\{z\}.*\{\\\z\}', text)
        for s in r:
            flag = s
            flag = flag.replace('{z}','')
            flag = flag.replace('{\z}','')
            self.set_flag(flag)
            text = text.replace(s,'')
        return text

    def set_flag(self, flag, value=1):
        if flag in self.flags:
            self.flags[flag] = value
        self.update_data()
    
    def unset_flag(self, flag):
        f = self.flags.get(flag)
        if f:
            self.flags[flag] = 0
        self.update_data()
    
    def match_flag(self, flag, value):
        if flag in self.flags:
            return self.flags[flag] == value
        return False

    def get_player(self):
        return self.player
    
    def join_chat(self, person):
        print("")
        character = self.character_book[person]
        if character:
            character.begin_chat()
        else:
            print("Could not find " + person + " in this domain!\n")
    
    def display_help(self):
        print(self.help_text)
    
    def display_entities(self):
        print(self.player.get_current_location().get_display_entities())

    def exit_game(self):
        sys.exit()

    def load_flags(self):
        with open("data/flags.txt") as file:
            for line in file:
                line = line.strip().rstrip('\n')
                new_line = line.split("=")
                self.flags[new_line[0]] = int(new_line[1].strip())

    def execute(self, command):
        if (command.replace(' ', '') == ""):
            return False
            
        command = command.strip()
        if command in self.default_commands.keys():
            self.default_commands[command]()
            return True

        if self.player.execute(command):
            return True

        return self.player.get_current_location().run_command(command)
    
    def reconnect_player(self):
        print("")
        print("Reconnecting ...")
        self.simulate_load(50,50,0.05,"...Connecting to <"+self.player.get_current_location().name+">",finished="DONE                                       ")
        time.sleep(0.2)
        print("")
        self.update_data()
        self.player.display_region()


def main():
    game = Game()
    game.start()
    while True:
        game.update()

if __name__ == "__main__":
    main()