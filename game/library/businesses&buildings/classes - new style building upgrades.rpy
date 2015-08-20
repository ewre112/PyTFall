init -9 python:
    #################################################################
    # BUILDING UPGRADE CLASSES
    class BuildingUpgrade(_object):
        """
        BaseClass for any building expansion!
        """
        def __init__(self, name="", instance=None, desc="", img="", build_effort=0, materials=None, in_slots=1, ex_slots=0, cost=0):
            self.name = name # name, a string.
            self.instance = instance # Building this upgrade belongs to.
            self.desc = desc # description, a string.
            self.img = img # Ren'Py path leading the an image, a string.
            
            self.build_effort = build_effort # Effort it takes to build this upgrade. 0 for instant.
            if not materials:
                self.materials = {} # Materials required to build this upgrade. Empty dict for none.
            else:
                self.materials = materials
            self.in_slots = in_slots # Internal slots
            self.ex_slots = ex_slots # External slots
            self.cost = cost # Price in gold.
            
            self.jobs = set() # Jobs this upgrade can add. *We add job instances here!
            self.workers = set() # List of on duty characters.
            
            self.habitable = False
            self.workable = False
        
        @property
        def env(self):
            # SimPy and etc follows (L33t stuff :) ):
            return self.instance.env
        
        def log(self, item):
            # Logs the text to log...
            self.instance.nd_events_report.append(item)
            
        def has_workers(self, amount=1):
            # Checks if there is a worker(s) availible.
            return False
            
        def get_workers(self, amount=1):
            # Finds a best match for workers and returns them...
            return None
            
        def requires_workers(self, amount=1):
            """
            Returns True if this upgrade requires a Worker to run this job.
            Example: Brothel
            Strip Club on the other hand may nor require one or one would be requested later.
            It may be a better bet to come up with request_worker method that evaluates the same ealier, we'll see.
            """
            return False
            
        def run_nd(self):
            # Runs at the very start of execusion of SimPy loop during the next day.
            return
            
        @property
        def all_occs(self):
            s = set()
            for i in self.jobs:
                s = s | i.all_occs
            return s
        
        
    class MainUpgrade(BuildingUpgrade):
        """
        Usually suggests a business of some kind and unlocks jobs and other upgrades!
        """
        def __init__(self, *args, **kwargs):
            super(MainUpgrade, self).__init__(*args, **kwargs)
            
            
    class BrothelBlock(MainUpgrade):
        def __init__(self, name="Brothel", instance=None, desc="Rooms to freck in!", img="content/buildings/upgrades/room.jpg", build_effort=0, materials=None, in_slots=2, cost=500, **kwargs):
            super(BrothelBlock, self).__init__(name=name, instance=instance, desc=desc, img=img, build_effort=build_effort, materials=materials, cost=cost, **kwargs)
            self.capacity = in_slots
            self.jobs = set([simple_jobs["Whore Job"], simple_jobs["Testing Job"]])
            self.workable = True
            
            # SimPy and etc follows (L33t stuff :) ):
            self.res = None # Restored before every job...
            self.time = 5 # Same
            
        def has_workers(self):
            return list(i for i in store.nd_chars if self.all_occs & i.occupations)
            
        def requires_workers(self, amount=1):
            return True
            
        def get_workers(self, amount=1):
            """
            This is quite possibly an overkill for this stage of the game development.
            """
            workers = list()
            
            # First gets the workers assigned directly to this upgrade as a priority.
            priority = list(i for i in store.nd_chars if i.workplace == self and self.all_occs & i.occupations)
            for i in range(amount):
                try:
                    workers.append(priority.pop())
                except:
                    break
            
            if len(workers) < amount:
                # Next try to get anyone availible:
                anyw = list(i for i in store.nd_chars if self.all_occs & i.occupations)
                for i in range(amount-len(workers)):
                    try:
                        workers.append(anyw.pop())
                    except:
                        break
                        
            if len(workers) == amount:
                if len(workers) == 1:
                    return workers.pop()
            # When we'll have jobs that require moar than one worker, we'll add moar code here.
            
        def run_nd(self):
            self.res = simpy.Resource(self.env, self.capacity)
            
        def request(self, client):
            with self.res.request() as request:
                yield request
                        
                # All is well and we create the event
                temp = "{} and {} enter the room at {}".format(client.name, store.char.name, self.env.now)
                self.log(temp)
                
                yield self.env.process(self.run_job(client, store.char))
                
                temp = "{} leaves at {}".format(client.name, self.env.now)
                self.log(temp)
                
        def run_job(self, client, char):
            """
            This should be a job...
            """
            yield self.env.timeout(self.time)
            if config.debug:
                temp = "Debug: {} Brothel Resource in use!".format(set_font_color(self.res.count, "red"))
                self.log(temp)
            
            temp = "{} and {} did their thing!".format(set_font_color(char.name, "pink"), client.name)
            self.log(temp)
            store.client = client
            store.char = char
            char.action()
            
            # We return the char to the nd list:
            store.nd_chars.insert(0, char)
            
            
    class StripClub(MainUpgrade):
        def __init__(self, name="Strip Club", instance=None, desc="Exotic Dancers go here!", img="content/buildings/upgrades/strip_club.jpg", build_effort=0, materials=None, in_slots=5, cost=500, **kwargs):
            super(StripClub, self).__init__(name=name, instance=instance, desc=desc, img=img, build_effort=build_effort, materials=materials, cost=cost, **kwargs)
            self.jobs = set([simple_jobs["Striptease Job"]])
            self.workable = True
            
            self.capacity = in_slots
            self.active = set() # On duty Strippers
            
            # SimPy and etc follows (L33t stuff :) ):
            self.res = None # Restored before every job...
            self.time = 5 # Same
            
            self.earned_cash = 0
            
        def run_nd(self):
            self.res = simpy.Resource(self.env, self.capacity)
            
        def request(self, client):
            with self.res.request() as request:
                yield request
                
                # All is well and we create the event
                temp = "{} enters the Strip Club at {}".format(client.name, self.env.now)
                self.log(temp)
                
                yield self.env.process(self.run_job(client, store.char))
                
                temp = "{} leaves the Club at {}".format(client.name, self.env.now)
                self.log(temp)
                
        def run_job(self, client, char):
            yield self.env.timeout(self.time)
            self.earned_cash += 100
            if config.debug:
                temp = "Debug: {} Strip Club Resource currently in use/ Cash earned: {}!".format(set_font_color(self.res.count, "red"), self.earned_cash)
                self.log(temp)
            
            
    class Bar(MainUpgrade):
        """
        Bar Main Upgrade.
        """
        def __init__(self, name="Bar", instance=None, desc="Serve drinks and snacks to your customers!", img="content/buildings/upgrades/bar.jpg", build_effort=0, materials=None, in_slots=3, cost=500, **kwargs):
            super(Bar, self).__init__(name=name, instance=instance, desc=desc, img=img, build_effort=build_effort, materials=materials, cost=cost, **kwargs)
            self.jobs = set(["Waitress"])
            self.workable = True
            
            
    class Garden(MainUpgrade):
        def __init__(self, name="Garden", instance=None, desc="Relax!", img="content/buildings/upgrades/garden.jpg", build_effort=0, materials=None, in_slots=0, ex_slots=2, cost=500, **kwargs):
            super(Garden, self).__init__(name=name, instance=instance, desc=desc, img=img, build_effort=build_effort, materials=materials, cost=cost, **kwargs)
            
            
    class MainHall(MainUpgrade):
        def __init__(self, name="Main Hall", instance=None, desc="Reception!", img="content/buildings/upgrades/main_hall.jpg", build_effort=0, materials=None, in_slots=0, ex_slots=2, cost=500, **kwargs):
            super(MainHall, self).__init__(name=name, instance=instance, desc=desc, img=img, build_effort=build_effort, materials=materials, cost=cost, **kwargs)
            self.jobs = set()
            
            
    class WarriorQuarters(MainUpgrade):
        def __init__(self, name="Warrior Quarters", instance=None, desc="Place for Guards!", img="content/buildings/upgrades/guard_qt.jpg", build_effort=0, materials=None, in_slots=2, ex_slots=1, cost=500, **kwargs):
            super(WarriorQuarters, self).__init__(name=name, instance=instance, desc=desc, img=img, build_effort=build_effort, materials=materials, cost=cost, **kwargs)
            self.jobs = set(["Guard"])
            
            
    class SlaveQuarters(MainUpgrade):
        def __init__(self, name="Slave Quarters", instance=None, desc="Place for slaves to live in!", img="content/buildings/upgrades/guard_qt.jpg", build_effort=0, materials=None, in_slots=2, ex_slots=0, cost=500, **kwargs):
            super(SlaveQuarters, self).__init__(name=name, instance=instance, desc=desc, img=img, build_effort=build_effort, materials=materials, cost=cost, **kwargs)
            self.rooms = in_slots
            
    # UPGRADES = [Bar(), BrothelBlock(), StripClub(), Garden(), MainHall(), WarriorQuarters(), SlaveQuarters()]
            
