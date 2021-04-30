import re
import random

class Website:
    def __init__(self, f, loaded=False):
        self.code_loaded = loaded
        self.data = ""
        self.code = dict()
        try:
            with open("data/region_sites/"+f, 'r') as file:
                current_code = 'null'
                found_code = False
                for line in file:
                    nline = line.rstrip('\n')
                    if found_code:
                        if nline == "{code}":
                            found_code = False
                        else:
                            if nline.endswith(';'):
                                c = nline.rstrip(';')
                                self.code[c] = []
                                current_code = c
                            else:
                                self.code[current_code].append(nline)
                    elif nline != "{code}":
                        self.data += line
                    else:
                        found_code = True
        except:
            self.data = "\nINVALID\n"

    def get_data(self):
        return self.data
    
    def get_code(self):
        self.code_loaded = True
        return(self.code)

class Flag_Proc:
    def __init__(self, flag, value, site):
        self.flag = flag
        self.value = value
        self.site = site

class Flag_Lock:
    def __init__(self, flag, value, saying):
        self.flag = flag
        self.value = value
        self.saying = saying

class Region:
    def __init__(self, name, default_site, game):
        self.first_load = True
        self.name = name
        self.default_site = default_site
        self.site = default_site
        self.description = ""
        self.examine_text = ""
        self.detail = ""
        self.valid_commands = {"examine":self.examine_region,"look":self.detail_region,"connect":self.connect}
        self.action_words = {}
        self.characters = {}
        self.objects = {}
        self.connected_regions = {}
        self.game = game
        self.loaded = False
        self.required_flags = []
        self.procs = []
        self.locks = []
        self.forced_lock = False

    def pre_load(self):
        site = Website(self.site, self.loaded)
        self.description = self.game.load_text(site.get_data())
        if not site.code_loaded:
            self.load_code(site)
        self.loaded = True
        if self.check_required_flags():
            self.load()
        
    def load(self):
        for c in self.game.get_player().followers.values():
            c.goto(self)
        self.game.get_player().update()
        self.game.get_player().current_location = self
        self.update_and_print()
    
    def load_code(self, site):
        for k, v in site.get_code().items():
            getattr(self, 'l_' + str(k),self.l_none)(v)

    def change_site(self, site):
        self.loaded = False
        self.site = site
        self.characters = dict()
        self.action_words = dict()
        self.objects = dict()
        self.connected_regions = dict()
        self.required_flags = []
        self.procs = []
        self.locks = []
        self.forced_lock = False
        if self.game.get_player().current_location == self:
            self.pre_load()

    def check_required_flags(self):
        for lock in self.required_flags:
            if not self.game.match_flag(lock.flag,lock.value):
                print(lock.saying)
                return False
        return True

    def l_required_flags(self, v):
        for flag in v:
            new_flag = flag.split('|')
            self.required_flags.append(Flag_Lock(new_flag[0],int(new_flag[1]),self.game.load_text(new_flag[2])))
    def l_flag_proc(self, v):
        for flag in v:
            new_flag = flag.split('|')
            self.procs.append(Flag_Proc(new_flag[0],int(new_flag[1]),new_flag[2]))
    def l_locked(self, v):
        for flag in v:
            new_flag = flag.split('|')
            self.locks.append(Flag_Lock(new_flag[0],int(new_flag[1]),self.game.load_text(new_flag[2])))
    def l_examine_text(self, v):
        self.examine_text = self.game.load_text("".join(v))
    def l_detail_text(self, v):
        self.detail = self.game.load_text("".join(v))
    def l_action_words(self, v):
        for word in v:
            new_words = word.split('|',1)
            self.action_words[new_words[0]] = new_words[1]
    def l_characters(self, v):
        for character in v:
            character = self.game.load_text(character)
            p_char = self.game.character_book.get(character)
            if p_char:
                self.add_character(p_char)
    def l_enemies(self, v):
        for enemy in v:
            enemy = self.game.load_text(enemy)
            p_enemy = self.game.character_book.get(enemy)
            if p_enemy:
                self.characters[p_enemy.name] = p_enemy
    def l_objects(self, v):
        for item in v:
            item = self.game.load_text(item)
            p_item = self.game.item_book.get(item)
            if p_item:
                self.objects[p_item.name] = p_item
    def l_connected_regions(self,v):
        for region in v:
            region = self.game.load_text(region)
            p_region = self.game.region_book.get(region)
            if p_region:
                self.connected_regions[p_region.name] = p_region
    def l_none(self, v):
        pass
    
    def unload(self):
        self.site = ""

    def add_object(self, item):
        self.objects[item.name] = item
    
    def remove_object(self, item):
        self.objects.pop(item.name)
    
    def add_character(self, character):
        self.characters[character.name] = character
        character.current_region = self

    def remove_character(self, character):
        self.characters.pop(character.name)
    
    def get_display_entities(self):
        output = "\n::::: Connections On <"+self.name+"> :::::"
        if len(self.characters) == 0:
            return output + "\nNo connections found...\n"
        return output + "\n" + "\n".join(map(str,list(self.characters.values()))) + "\n"

    def get_display_items(self):
        if len(self.objects) == 0:
            return ""
        item_list = []
        for i in list(self.objects.values()):
            if not i.hidden:
                item_list.append(str(i))
        if len(item_list) > 0:
            return "\n> " + "\n> ".join(item_list) + "\n"
        return ""
    
    def check_locked(self):
        if len(self.locks) != 0:
            for lock in self.locks:
                l = self.game.flags.get(lock.flag, 'none')
                if l == 'none':
                    continue
                if l == lock.value:
                    print(lock.saying)
                    return True
            return self.forced_lock
        return self.forced_lock
    
    def run_command(self, command):
        ncm = command.lower()
        if ncm in self.valid_commands:
            self.valid_commands[ncm]()
            return True

        if command in self.action_words:
            print(self.game.load_text(self.action_words[command]))
            return True
        
        if (command in self.connected_regions):
            self.connected_regions[command].connect()
            return True

        broken_command = command.split()
        verb = broken_command[0].lower()

        if len(broken_command) > 1:
            noun = " ".join(broken_command[1:])
            item_check = self.check_name_list(self.objects, verb, noun)
            if item_check:
                return item_check
            
            character_check = self.check_name_list(self.characters, verb, noun)
            if character_check:
                return character_check
            
            region_check = self.check_name_list(self.connected_regions, verb, noun)
            if region_check:
                return region_check

            if noun == self.name:
                return self.execute(verb)

        print("'" + command + "'" + " was not found...")
        return False
    
    def connect(self):
        locked = self.game.get_player().current_location.check_locked()
        if self.game.get_player().current_location != self and not locked:
            self.pre_load()
        if self.game.get_player().current_location.forced_lock:
            print("There is something blocking your connection hop!")


    def execute(self, command):
        ncm = command.lower()
        if ncm in self.valid_commands:
            self.valid_commands[command]()
            return True
        print("Invalid request " + command + " on " + self.name)
        return False

    def check_name_list(self, some_list, verb, noun):
        if noun in some_list:
            some_list[noun].execute(verb)
            return True
        return False

    def examine_region(self):
        print(self.examine_text)
    
    def detail_region(self):
        print(self.detail)
    
    def update(self):
        for character in self.characters.values():
            character.update()
        for item in self.objects.values():
            item.update()
        for proc in self.procs:
            if self.game.match_flag(proc.flag, proc.value):
                self.change_site(proc.site)

    def update_and_print(self):
        self.update()
        print(self)

    def __str__(self):
        return self.description + self.get_display_items() + self.get_display_entities()

    def __repr__(self):
        return self.description + self.get_display_items() + self.get_display_entities()

class Slide(Region):
    def __init__(self, name, default_site, game):
        super().__init__(name, default_site, game)
    def connect(self):
        if self.game.get_player().current_location != self and not self.game.get_player().current_location.check_locked() and self.check_required_flags():
            print("")
            self.game.simulate_load(50,50,0.05,"...Sliding",False,False,'e',' ','W',"!                               ")
            print("")
            self.game.region_book.get('meadow.lily.town').connect()

class Secret(Region):
    def __init__(self, name, default_site, game):
        super().__init__(name, default_site, game)
        self.secrets = [
            "I actually like the black lotus... Although the outer edge of town scares me.",
            "I wish I told him how I felt before he left... All I can do is hope he comes back...",
            "I still cry when I watch Living with Lizards 2.",
            "I've lied so much I don't know when I'm lying or not any more.",
            "I have done null bytes."
            "I got lost in the outer edge without a beacon for 40 days... on purpose",
            "Puddle still slippin. Lash out I'll give you a lippin.",
            "I hate penguins! I think they are ugly!",
            "I sleep instead of doing homework. I torrent the answers on benice2me during tests as well.",
            "I am a shallow person.",
            "I hate this town. I can't wait to leave.",
            "Ava created the beast. I'm sure of it!",
            "Does anyone actually know who to vote for other than Chr0n0s. Guy is getting old dude... does he even have aging off?",
            "I think {name} was taken offline because he is mortal... I hate him even more now"
        ]
        self.valid_commands.update({"get":self.get_secrets,"get secrets":self.get_secrets,"password":self.get_password})
        self.found_pass = False

    def get_secrets(self):
        print(self.game.load_text(random.choice(self.secrets)))
    
    def get_password(self):
        if not self.found_pass:
            self.add_object(self.game.item_book.get('pass'))
            print("Nice guess! - Se7")
            self.found_pass = True

class Chip(Region):
    def __init__(self, name, default_site, game):
        super().__init__(name, default_site, game)
        self.valid_commands.update({"jump":self.jump})
        
    def jump(self):
        print("")
        self.game.simulate_load(40,40,0.1,"...Falling!!!!!!!",False,False,'a',' ','A',"!                               ")
        print("")
        self.game.region_book.get('outerspace.lily.town').connect()