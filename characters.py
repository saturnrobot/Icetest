import re
import time

class ChatMessage:
    def __init__(self, name, key, message, connected_keys=None, instant=None, leave=False, any_word=None, external=False, function=None):
        self.name = name
        self.key = key
        self.message = message
        self.connected_keys = dict()
        if connected_keys:
            c_split = connected_keys.split('|')
            for ck in c_split:
                n_split = ck.split(':')
                self.connected_keys[n_split[0]] = n_split[1]
        self.any_word = any_word
        self.leave = leave
        self.function = function
        self.instant = instant
        self.external = external
    
    def check_keys(self, word):
        if self.any_word:
            for key in self.connected_keys.keys():
                if word in key.split(';'):
                    return self.connected_keys[key]
            return self.any_word
        for key in self.connected_keys.keys():
            if word in key.split(';'):
                return self.connected_keys[key]
        return "unknown"
    
    def print_word(self):
        time.sleep(0.5)
        if self.message == "{none}":
            return
        elif not self.external:
            print("["+self.name+"]: " + self.message)
        else:
            print(self.message)

    def __repr__(self):
        return self.message

class Character:
    def __init__(self, name, path, default, examine, game):
        self.name = name
        self.game = game
        self.message = examine
        self.chat_messages = {}
        self.current_message = None
        self.saved_message = None 
        self.left = False
        self.status = "Just chillin"
        self.valid_commands = {"chat":self.begin_chat, "examine":self.examine}
        self.functions = {"follow":self.follow,"unfollow":self.unfollow}
        self.arg_functions = {"goto":self.goto_with_name, "set_flag":self.set_flag, "give":self.give}
        self.current_region = None
        self.loaded_file = ''
        self.path = path
        self.default = default
    
    def load_chat_file(self, file):
        if self.loaded_file == file: return
        self.chat_messages = dict()
        with open(self.path+file, 'r') as f:
            stored_key = None
            stored_message = None
            stored_args = None
            for line in f:
                line = line.rstrip('\n')
                if line.replace(' ', '') == "":
                    continue
                elif line.startswith('status='):
                    self.status = self.game.load_text(line.split('status=',1)[1])
                elif not stored_key and (re.findall("\|.*?\|", line)[0]) == line:
                    stored_key = line.replace('|',"")
                elif not stored_message:
                    stored_message = self.game.load_text(line)
                elif not stored_args:
                    stored_args = self.format_args(line.split(','))
                if stored_key and stored_message  and stored_args:
                    self.chat_messages[stored_key] = ChatMessage(self.name,stored_key,stored_message,stored_args[0],stored_args[1],stored_args[2],stored_args[3],stored_args[4],stored_args[5])
                    stored_key = None
                    stored_message = None
                    stored_args = None
        self.loaded_file = file

    def format_args(self, a):
        if a[0] == '0':
            a[0] = None
        if a[1] == '0':
            a[1] = None
        if a[2] == '0':
            a[2] = False
        else:
            a[2] = True
        if a[3] == '0':
            a[3] = None
        if a[4] == '0':
            a[4] = False
        else:
            a[4] = True
        if a[5] == '0':
            a[5] = None
        return a

    def execute(self, command):
        ncm = command.lower()
        if ncm in self.valid_commands:
            self.valid_commands[command]()
            return True
        print("Cannot " + command + " on " + self.name)
        return False
    
    def update(self):
        self.load_chat_file(self.default)

    def begin_chat(self):
        print("")
        print(">>> YOU CONNECTED TO " + self.name.upper() + " <<<")
        self.load_chat()

    def load_chat(self):
        self.update()
        self.current_message = self.chat_messages["main"]
        self.saved_message = self.chat_messages["main"]
        self.chat(True)
    
    def follow(self):
        self.game.get_player().follow(self)
    
    def unfollow(self):
        self.game.get_player().unfollow(self)

    def goto(self, region):
        if self.current_region:
            if self.current_region != region:
                self.current_region.remove_character(self)
        region.add_character(self)

    def goto_with_name(self, region_name):
        if region_name in self.game.region_book:
            self.goto(self.game.region_book[region_name])
    def set_flag(self, flag):
        new_f = flag.split('@')
        if len(new_f) > 1:
            self.game.flags[new_f[0]] = int(new_f[1])
        else:
            self.game.flags[flag] = 1
        self.update()

    def give(self, item):
        p_item = self.game.item_book.get(item)
        if p_item:
            self.game.get_player().add_to_inv(p_item)
            print("[!NOTICE!]: " + self.name + " uploaded " + p_item.name + " to your inventory!")

    def handle_function(self, function):
        if not function: return False
        functions = function.split(';')
        for f in functions:
            if f in self.functions:
                self.functions[f]()
            else:
                s_function = f.split(':')
                if len(s_function) > 1:
                    if s_function[0] in self.arg_functions:
                        self.arg_functions[s_function[0]](s_function[1])
        return True

    def chat(self, main=False):
        while True:
            no_words = False

            if self.handle_function(self.current_message.function):
                self.current_message.function = None

            if main:
                self.current_message.print_word()
                main = False
                if self.current_message.instant:
                    message = self.chat_messages[self.current_message.instant]
                    self.current_message = message
                    self.saved_message = message
                    continue
            elif not self.left:
                self.current_message.print_word()
                if self.current_message.leave:
                    time.sleep(1)
                    print(">>> " + self.name.upper() + " HAS LEFT THE CHATROOM! <<<")
                    self.left = True
                elif self.current_message.instant:
                    message = self.chat_messages[self.current_message.instant]
                    self.current_message = message
                    self.saved_message = message
                    continue
            if not self.saved_message.connected_keys:
                no_words = True

            while True:
                new_word = str(input('['+self.game.get_player().get_name()+']'': ')).strip()
                if (new_word.replace(' ', '') != "") or no_words:
                    if new_word=="disconnect" or new_word=="d":
                        print(">>> DISCONNECTED FROM " + self.name.upper() + " <<<")
                        self.game.get_player().disconnect_chat()
                        self.left = False
                        return
                    else:
                        if not self.left:
                            message = self.chat_messages[self.saved_message.check_keys(new_word)]
                            self.current_message = message
                            if self.current_message.key != "unknown":
                                self.saved_message = message
                    break
                else:
                    print("MESSAGE NOT SENT! Reason: empty.\n(Hint: Type [disconnect] to leave chat)")

    def examine(self):
        print(self.game.load_text(self.message))

    def __str__(self):
        return "["+self.name+"]" + " - " + self.status


class Alice(Character):
    def __init__(self, name, path, default, examine, game):
        super().__init__(name, path, default, examine, game)
    
    def update(self):
        if self.game.flags['alice1'] == 0:
            self.load_chat_file('first_alice.txt')
        elif self.game.flags['alice5'] == 1 or self.game.flags['act1'] == 1:
            self.load_chat_file('alice_dead.txt')
        elif self.game.flags['alice4'] == 1 and self.game.flags['alice_beast'] == 0:
            c = self.game.character_book['SBeAST']
            c.goto_with_name('m1st.lily.town')
            self.load_chat_file('alice_beast.txt')
            self.game.flags['alice_beast'] = 1
        elif self.game.flags['alice4'] == 1:
            self.load_chat_file('alice_beast.txt')
        elif self.game.flags['alice3'] == 1 and self.game.get_player().current_location.name == '6chip.lily.town':
            self.load_chat_file('alice_6chip.txt')
        elif self.game.flags['alice3'] == 1:
            self.load_chat_file('alice_after_zung.txt')
        elif self.game.flags['alice2'] == 1:
            self.load_chat_file('alice_zung.txt')
        elif self.game.flags['alice_key_uploaded'] == 1:
            self.load_chat_file('alice_key_done.txt')
        elif self.game.flags['alice_key_uploaded'] == 0:
            self.load_chat_file('alice_key_wait.txt')

class Gus(Character):
    def __init__(self, name, path, default, examine, game):
        super().__init__(name, path, default, examine, game)
    
    def update(self):
        if self.game.flags['progression'] <= 1:
            self.load_chat_file('gus.txt')
        elif self.game.flags['got_dream'] == 1:
            self.load_chat_file('gusend.txt')
        else:
            self.load_chat_file('gus2.txt')

class Chronos(Character):
    def __init__(self, name, path, default, examine, game):
        super().__init__(name, path, default, examine, game)
    
    def update(self):
        if self.game.flags['chronos1'] == 0 and self.game.flags['act1'] == 0:
            self.load_chat_file('chronos_lib.txt')
        elif self.game.flags['chronos2'] == 1:
            self.load_chat_file('chronos_q2.txt')
        elif self.game.flags['act1'] == 1:
            self.load_chat_file('chronos_b1.txt')
        elif self.game.flags['chronos1'] == 1:
            self.load_chat_file('chronos_q.txt')

class Ava(Character):
    def __init__(self, name, path, default, examine, game):
        super().__init__(name, path, default, examine, game)
    
    def update(self):
        if self.game.flags['ava1'] == 0:
            self.load_chat_file('ava.txt')
        else:
            self.load_chat_file('ava_q.txt')

class Klaus(Character):
    def __init__(self, name, path, default, examine, game):
        super().__init__(name, path, default, examine, game)
    
    def update(self):
        if self.game.get_player().current_location.name == "null.lily.town":
            self.unfollow()
            self.status = "Hacking... (check it out bro... [chat] is open...)"
            self.load_chat_file('klaus2.txt')
        else:
            self.load_chat_file('klaus1.txt')