from helpers import *
import random

class Player:
    def __init__(self, name, spawn, game):
        self.name = name
        self.current_location = spawn
        self.hp = 10
        self.dhp = 10
        self.atk = 3
        self.reg = 3
        self.moves = {"OVERFLOW":self.attack, "RECONNECT":self.heal}
        self.inv = {}
        self.game = game
        self.followers = {}
    
    def execute(self, command):
        broken_command = command.split()
        verb = broken_command[0].lower()
        if (len(broken_command) > 1) and verb != 'download':
            noun = " ".join(broken_command[1:])
            if noun in self.inv:
                self.inv[noun].execute(verb)
                return True      
        return False

    def update(self):
        for item in self.inv.values():
            item.update()
        for c in self.followers.values():
            c.update()
    
    def fight_turn(self, enemy):
        print("")
        print(":::: IC3_PWN is >>>> ACTIVE <<<< ::::")
        while True:
            move_string = ""
            for k in self.moves:
                move_string += "["+k + "] "
            print("Valid moves: " + move_string)
            attack = str(input("Enter an attack: ")).strip()
            if attack.replace(' ', '') == "":
                print("Empty.")
                continue
            move = self.moves.get(attack.upper())
            if move:
                enemy = self.moves[attack.upper()](enemy)
                break
            print("No move called " + attack.upper())
        return enemy

    def add_to_inv(self, item):
        self.inv[item.name] = item

    def remove_from_inv(self, item):
        self.inv.pop(item.name)
    
    def item_in_inv(self, item):
        return item in list(self.inv.values())
    
    def get_name(self):
        return self.name
    
    def get_current_location(self):
        return self.current_location
    
    def move(self, location):
        self.current_location = location

    def attack(self, enemy):
        dam = random.randint(0,self.atk)
        if dam == 0:
            enemy.hud.add_to_log("Failed to connect!")
        else:
            enemy.hp -= dam
            if enemy.hp < 0:
                enemy.hp = 0
            enemy.hud.add_to_log("CONNECTION SUCCESSFUL; Did " + str(dam) + " to " + enemy.name + "'s connection!")
        return enemy

    def heal(self, enemy):
        dam = random.randint(0,self.reg)
        if dam == 0:
            enemy.hud.add_to_log("Failed to restore connection!")
        else:
            self.hp += dam
            if self.hp > self.dhp:
                self.hp = self.dhp
            enemy.hud.add_to_log("You restore some connection!")
        return enemy
    
    def alive(self):
        if self.hp <= 0:
            self.hp = self.dhp
            return False
        return True
    
    def display_region(self):
        print(self.current_location)

    def disconnect_chat(self):
        print("")
    
    def follow(self, character):
        self.followers[character.name] = character
    
    def unfollow(self, character):
        if character.name in self.followers:
            self.followers.pop(character.name)

    def display_inv(self):
        print("Currently in your storage:")
        if len(self.inv) >= 1:
            for item in self.inv:
                print("-> " + item)
        else:
            print("empty...")
