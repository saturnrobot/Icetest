class Item:
    def __init__(self, key, name, message, description, game):
        self.key = key
        self.name = name
        self.message = message
        self.description = description
        self.valid_commands = {"download":self.take, "upload":self.drop, "examine":self.examine}
        self.game = game
        self.hidden = False

    def execute(self, command):
        ncm = command.lower()
        if ncm in self.valid_commands:
            self.valid_commands[command]()
            return True
        print("Invalid action " + command + " on " + self.name)
        return False
    
    def update(self):
        pass

    def drop(self):
        if not self.game.get_player().item_in_inv(self):
            print("Can't upload " + self.name + " not in invrentory (Try [download]ing it first)")
            return
        self.drop_effect()
        self.game.get_player().current_location.add_object(self)
        self.game.get_player().remove_from_inv(self)
        print("You uploaded " + self.name + " to " + self.game.get_player().current_location.name)
    
    def drop_effect(self):
        pass
    
    def take(self):
        self.game.get_player().current_location.remove_object(self)
        self.game.get_player().add_to_inv(self)
        self.take_effect()
        print("You download " + self.name)
    
    def take_effect(self):
        pass
    
    def get_name(self):
        return self.name

    def examine(self):
        print(self.description)

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message

class gpgkey(Item):
    def __init__(self, key, name, message, description, game):
        super().__init__(key, name, message, description, game)
    
    def take_effect(self):
        self.game.set_flag('have_alice_key')
    
    def drop_effect(self):
        if self.game.get_player().current_location.name == "m1st.lily.town" and self.game.match_flag("alice_key_uploaded",0):
            self.game.flags['progression'] += 1
            self.game.set_flag('alice_key_uploaded')
        self.game.unset_flag('have_alice_key')
        
class pgpgkey(Item):
    def __init__(self, key, name, message, description, game):
        super().__init__(key, name, message, description, game)

class iceecream(Item):
    def __init__(self, key, name, message, description, game):
        super().__init__(key, name, message, description, game)
        self.valid_commands.update({'taste':self.taste})
    
    def taste(self):
        print("ooh it's cyber_choc flavored!")

class poepoe(Item):
    def __init__(self, key, name, message, description, game):
        super().__init__(key, name, message, description, game)
        self.valid_commands.update({'pet':self.pet})
    
    def pet(self):
        print("You pet PoePoe. PoePoe closes its eyes in enjoyment.")
    
    def take_effect(self):
        self.game.get_player().atk += 2
        self.game.set_flag('have_poepoe')
    
    def drop_effect(self):
        self.message = "[PoePoe] is sleeping nearby."
        self.game.get_player().atk -= 2
        self.game.unset_flag('have_poepoe')

class paw(Item):
    def __init__(self, key, name, message, description, game):
        super().__init__(key, name, message, description, game)
        self.valid_commands.update({'read':self.read})

    def read(self):
        self.game.get_player().hp = self.game.get_player().dhp
        print("You gain some hope! You feel well connected!")
    
    def drop_effect(self):
        self.message = "[Pastoral Works] is appended here."

class kidspass(Item):
    def __init__(self, key, name, message, description, game):
        super().__init__(key, name, message, description, game)
    
    def take_effect(self):
        self.game.set_flag('kids_pass')
    
    def drop_effect(self):
        self.game.unset_flag('kids_pass')

class mew(Item):
    def __init__(self, key, name, message, description, game):
        super().__init__(key, name, message, description, game)
        self.valid_commands.update({'drink':self.drink})
        self.empty = False

    def drink(self):
        if not self.empty:
            print("... That hit the spot! Such a wonderful taste!")
            self.message = "An empty [mew_choc.flav] waits for a refill"
            self.empty = True
        else:
            print("There's nothing left :(")
class cutie(Item):
    def __init__(self, key, name, message, description, game):
        super().__init__(key, name, message, description, game)
        self.hidden = True
        self.valid_commands.update({'sell':self.sell})
    
    def take_effect(self):
        self.hidden = False
        
    def sell(self):
        cur_loc = self.game.get_player().current_location
        if cur_loc.name == "sadboyz.lily.town":
            cur_loc.add_character(self.game.character_book['PuddleBoyStarz'])
            print("A new connection appeared!")
        else:
            print("No one is desperate enough to buy this from me.")

class keyitem(Item):
    def __init__(self, key, name, message, description, game):
        super().__init__(key, name, message, description, game)
    
    def take_effect(self):
        self.game.flags['progression'] += 1
        if self.game.get_player().current_location.name == "lost.lily.town":
            self.game.flags['key_count'] -= 1
        self.game.update_data()
    
    def drop_effect(self):
        self.game.flags['progression'] -= 1
        if self.game.get_player().current_location.name == "lost.lily.town":
            self.game.flags['key_count'] += 1
        self.game.update_data()

class keyitemf(Item):
    def __init__(self, key, name, message, description, game):
        super().__init__(key, name, message, description, game)
    
    def take_effect(self):
        if self.game.get_player().current_location.name == "lost.lily.town":
            self.game.flags['key_count'] -= 1
        else:
            self.game.flags['progression'] += 1
        if self.game.flags['CPU14_defeated'] == 0:
            e = self.game.character_book['CPU14']
            e.fight_lock = False
            e.begin_fight()
        self.game.update_data()
    
    def drop_effect(self):
        if self.game.get_player().current_location.name == "lost.lily.town":
            self.game.flags['key_count'] += 1
        else:
            self.game.flags['progression'] -= 1
        self.game.update_data()

class glow(Item):
    def __init__(self, key, name, message, description, game):
        super().__init__(key, name, message, description, game)
        self.valid_commands.update({"shake":self.shake})
        self.shaken = False
    
    def take_effect(self):
        if self.game.get_player().current_location.name == "paul.lily.town":
            self.game.unset_flag('glow_uploaded')
    def drop_effect(self):
        if not self.shaken:
            self.message = "An [X-Glow Stick] faintly glows..."
        else:
            self.message = "An [X-Glow Stick] gives off a strong multi-colour glow!"
        if self.game.get_player().current_location.name == "paul.lily.town" and self.shaken:
            self.game.set_flag('glow_uploaded')

    def shake(self):
        if self.game.get_player().item_in_inv(self):
            print("* You shake the X-Glow Stick. *")
            print("* It glows brightly again *")
            self.shaken = True
        else:
            print("Can't shake something not in your hand!")

class dream(Item):
    def __init__(self, key, name, message, description, game):
        super().__init__(key, name, message, description, game)
    
    def drop_effect(self):
        if self.game.get_player().current_location.name == 'zclub.lily.town':
            self.game.set_flag('dream_uploaded')
            self.game.simulate_load(10,10,0.3,"...Uploading Cyberspace Daydream",finished="DONE                                  ")
            print("> Contribution cloned! You're welcome to connect to [dream.lily.town].")

class lotus(Item):
    def __init__(self, key, name, message, description, game):
        super().__init__(key, name, message, description, game)
    def take(self):
        if self.game.get_player().current_location.name != 'blacklotus.lily.town':
            super().take()
        else:
            print("The lotus denies your download request!")
        
    def drop_effect(self):
        if self.game.get_player().current_location.name == 'blacklotus.lily.town':
            self.game.flags['progression'] += 1
            self.game.set_flag('lotus_placed')
            self.game.get_player().current_location.add_character(self.game.character_book['Ava'])

class beacon(Item):
    def __init__(self, key, name, message, description, game):
        super().__init__(key, name, message, description, game)
        self.valid_commands.update({"use":self.use})
    
    def use(self):
        if self.game.get_player().item_in_inv(self):
            print("The beacon sends a transmission!")
            self.game.region_book['lily.town'].connect()
