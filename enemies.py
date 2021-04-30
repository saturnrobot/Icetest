from characters import *
from helpers import *
import random
import time

class Hud:
    def __init__(self):
        self.c = ""
        self.e = ""
        self.t = ""
        self.log = []

    def update_hud(self, enemy):
        player = enemy.game.get_player()
        self.c = player.name + ": Connection [" + "#"*player.hp + " "*(player.dhp - player.hp) + "]"
        self.e = enemy.name + ": Connection [" + "#"*enemy.hp + " "*(enemy.dhp - enemy.hp) + "]"
        self.t = "Connection: loaded (" + player.current_location.name + "/" + enemy.name + "); [ACTIVE]"
    
    def add_to_log(self, message):
        self.log.append("> " + message)

    def print_hud(self, enemy, delay=True):
        clearView()
        self.update_hud(enemy)
        print("$&#%$%$&@#&#$# HACKERSPACE #%&$#&%@#%@$@%")
        print("=====================================")
        print(self.c)
        print(self.e)
        print("=====================================")
        print(self.t)
        for m in self.log:
            print(m)
        if delay:
            time.sleep(1)

class BattleText:
    def __init__(self, keep, messages):
        if keep == '0':
            self.keep = False
        else:
            self.keep = True
        self.messages = messages.split('|')
        self.old_messages = []
    
    def get_message(self):
        if len(self.messages) >= 1:
            choice = random.choice(self.messages)
            if not self.keep:
                self.messages.remove(choice)
                self.old_messages.append(choice)
            return choice
        return False
    def reload_messages(self):
        self.messages.extend(self.old_messages)

class Enemy(Character):
    def __init__(self, name, hp, atk, sayings, status, examine, game):
        self.name =  name
        self.game = game
        self.chat_messages = {}
        self.message = examine
        self.current_message = None
        self.saved_message = None
        self.left = False
        self.status = status
        self.valid_commands = {"hack":self.begin_fight,"examine":self.examine}
        self.functions = {}
        self.loaded_sayings = ""
        self.battle_sayings = self.load_battle_text(sayings)
        self.current_region = None

        self.hp = int(hp)
        self.dhp = int(hp)
        self.atk = int(atk)
        self.hud = Hud()
        self.fight_lock = False
        self.attack_first = False
    
    def load_battle_text(self, file):
        if self.loaded_sayings == file: return
        sayings = dict()
        with open(file, 'r') as f:
            for line in f:
                line = line.rstrip('\n')
                n_line = line.split('=')
                sayings[n_line[0]] = BattleText(n_line[1], self.game.load_text(n_line[2]))
        self.loaded_sayings == file
        return sayings

    def execute(self, command):
        return super().execute(command)
    
    def update(self):
        pass
    
    def begin_fight(self):
        for i in self.battle_sayings.values():
            i.reload_messages()
        self.update()
        if not self.fight_lock:
            self.send_battle_text('e')
            self.hud.print_hud(self)
            if self.attack_first:
                self.fight(self, self.game.get_player())
            else:
                self.fight(self.game.get_player(), self)
        else:
            print("::::UNABLE TO CONNECT TO " + self.name.upper()+"::::")
    
    def fight(self, attacker, defender):
        while True:
            turn = attacker.fight_turn(defender)
            self.hud.print_hud(self)
            if not self.game.get_player().alive():
                self.end_fight(False)
                break
            elif not self.alive():
                self.end_fight(True)
                break
            if turn != attacker:
                defender = attacker
                attacker = turn
    
    def fight_turn(self, enemy):
        self.send_battle_text('a')
        self.send_battle_text(str(self.hp))
        self.hud.print_hud(self)
        return self.do_attack(enemy)

    def send_battle_text(self, key):
        text = self.battle_sayings.get(key, False)
        if text:
            m = text.get_message()
            if m:
                self.hud.add_to_log(m)
        
    def do_attack(self, enemy):
        dam = random.randint(0, self.atk)
        if dam == 0:
            self.hud.add_to_log(self.name + " failed to connect!")
        else:
            enemy.hp -= dam
            if enemy.hp < 0:
                enemy.hp = 0
            self.hud.add_to_log(self.name + " CONNECTION SUCCESSFUL; Did " + str(dam) + " to your connection!")
        return enemy
    
    def alive(self):
        if self.hp <= 0:
            self.hp = 0
            return False
        return True
    
    def end_fight(self, win):
        if win:
            self.send_battle_text('d')
            self.player_win()
            self.hud.print_hud(self)
            print("> !!!!!!!!!!!!!!! YOU DISCONNECTED " + self.name + " !!!!!!!!!!!!!!!")
            self.game.get_player().current_location.remove_character(self)
            self.game.flags[self.name+"_defeated"] += 1
        else:
            self.send_battle_text('w')
            self.hud.print_hud(self)
            print("> !!!!!!!!!!!!!!! DISCONNECTED! YOU LOST! !!!!!!!!!!!!!!!")
            self.game.flags[self.name+"_losses"] += 1
            self.game.reconnect_player()
        
        self.hp = self.dhp
        self.hud = Hud()

    def player_win(self):
        pass

    def __str__(self):
        return "!["+self.name+"]" + " - " + self.game.load_text(self.status) + "!"

class SBeast(Enemy):
    def __init__(self, name, hp, atk, sayings, status, examine, game):
        super().__init__(name, hp, atk, sayings, status, examine, game)

    def end_fight(self, win):
        rb = self.game.region_book
        ac = self.game.character_book['Alice']
        cc = self.game.character_book['Chr0n0s']
        spawn = rb.get('debug.hq.lily.town')
        ac.goto(spawn)
        cc.goto(spawn)
        self.game.get_player().current_location.remove_character(self)
        self.game.flags['progression'] += 1
        print("")
        self.game.simulate_load(50,50,0.05,"... Corrupting [mind.core]",finished="FAILED!                                ")
        print("ERROR: unable to reslove type MINIMAL to REALISTIC!")
        print("ABORT!")
        time.sleep(1)
        self.game.set_flag('act1')
        spawn.connect()

class Zung(Enemy):
    def __init__(self, name, hp, atk, sayings, status, examine, game):
        super().__init__(name, hp, atk, sayings, status, examine, game)
        self.multiply_chance = 100
        self.invalid_regions = ['none.lily.town', 'm1st.lily.town', 'slide.lily.town', 'den.lily.town']

    def do_attack(self, enemy):
        pick = random.randint(1,101)
        if pick > self.multiply_chance:
            return super().do_attack(enemy)
        spawn = random.choice(list(self.game.region_book.values()))

        if spawn == self.game.get_player().current_location:
            spawn = self.game.region_book['lily.town']
        else:
            for i in self.invalid_regions:
                if spawn == self.game.region_book[i]:
                    spawn = self.game.region_book['lily.town']
                    break

        new_zung = Zung(self.name, random.randint(3,4), random.randint(1,2), 'data/enemy_data/zung.txt', self.status, self.examine, self.game)
        new_zung.multiply_chance = random.randint(45,65)
        spawn.add_character(new_zung)
        self.hud.add_to_log(self.name + " multiplies. A new Zung has spawned somewhere on the lily.town domain!")
        spawn.forced_lock = True
        return enemy
    
    def player_win(self):
        self.game.get_player().current_location.forced_lock = False

class Sadboy(Enemy):
    def __init__(self, name, hp, atk, sayings, status, examine, game):
        super().__init__(name, hp, atk, sayings, status, examine, game)
    
    def do_attack(self, enemy):
        self.hud.add_to_log(self.name + " is spitting mad bars!")
        return enemy
    
    def player_win(self):
        item = self.game.item_book['e']
        self.game.get_player().current_location.add_object(item)
        self.hud.add_to_log(self.name + " dropped an " + item.name)

class CPU(Enemy):
    def __init__(self, name, hp, atk, sayings, status, examine, game):
        super().__init__(name, hp, atk, sayings, status, examine, game)
        self.fight_lock = True
        self.attack_first = True
    def update(self):
        if self.game.get_player().current_location.name == "null.lily.town":
            self.unfollow()
            self.status = "Hacking..."
    def end_fight(self, win):
        if win:
            self.send_battle_text('d')
            self.player_win()
            self.hud.print_hud(self)
            print("> CPU14 and K14us back off.")
            print("> Okay okay, it's yours now!")
            self.game.flags[self.name+"_defeated"] += 1
            self.follow()
            self.game.character_book['K14us'].follow()
            self.game.character_book['K14us'].status = "Take us to the lock!"
            self.status = "(Is following you)"
            self.fight_lock = True
        else:
            self.send_battle_text('w')
            self.hud.print_hud(self)
            print("> !!!!!!!!!!!!!!! DISCONNECTED! YOU LOST! !!!!!!!!!!!!!!!")
            self.game.flags[self.name+"_losses"] += 1
            i = self.game.get_player().inv.get('y.byte')
            if self.game.get_player().item_in_inv(i):
                i.drop()
            self.game.reconnect_player()
        
        self.hp = self.dhp
        self.hud = Hud()
class Beast(Enemy):
    def end_fight(self, win):
        if win:
            self.send_battle_text('d')
            self.player_win()
            self.hud.print_hud(self)
            self.game.get_player().current_location.remove_character(self)
            self.game.flags[self.name+"_defeated"] += 1
            print("!!!!!!!!!!!!!!!!!!! YOU WIN !!!!!!!!!!!!!!!!!!!")
        else:
            self.send_battle_text('w')
            self.hud.print_hud(self)
            print("> !!!!!!!!!!!!!!! DISCONNECTED! YOU LOST! !!!!!!!!!!!!!!!")
            self.game.flags[self.name+"_losses"] += 1
            self.game.reconnect_player()