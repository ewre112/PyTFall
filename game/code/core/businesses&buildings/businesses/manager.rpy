# Manager stuff goes here, will prolly be only one function but it doesn't fit anywhere else.
# This process should be ran first!
init -50 python:
    class ManagerData(object):
        def __init__(self):
            self.init_pep_talk = True
            self.cheering_up = True
            self.asks_clients_to_wait = True
            self.help_ineffective_workers = True # Bad performance still may get a payout.
            self.works_other_jobs = False

            self.manager = None
            # Calculated once at start of each working day (performance)
            self.manager_effectiveness = 0
            self.workers_rule = "normal"

            self.mlog = None # Manager job log

        @property
        def mjp(self):
            if self.manager:
                return self.manager.jobpoints
            else:
                return 0
        @mjp.setter
        def mjp(self, value):
            if self.manager:
                self.manager.jobpoints = value

init -5 python:
    class Manager(Job):
        """This is the manager Job, so far it just creates the instance we can use to assign the job.

        - Later we may use this to do mod stats and level up Managers somehow...
        """
        def __init__(self):
            super(Manager, self).__init__()
            self.id = "Manager"
            self.type = "Management"

            # Traits/Job-types associated with this job:
            self.occupations = ["Specialist"] # General Strings likes SIW, Combatant, Server...
            self.occupation_traits = [traits["Manager"]] # Corresponding traits...
            self.aeq_purpose = 'Manager'
            self.desc = "Manages your business, helping workers in various ways and improving their performance."

            self.base_skills = {"management": 80, "refinement": 20}
            self.base_stats = {"character": 40, "intelligence": 60}

            self.allowed_status = ["free"]


    def manager_process(env, building):
        manager = building.manager
        effectiveness = building.manager_effectiveness

        log = building.mlog
        log.append("{} is overseeing the building!".format(manager.name))
        log.append("")

        # Special bonus to JobPoints (aka pep talk) :D
        if building.init_pep_talk and effectiveness > 95 and manager.jobpoints >= 10:
            mp_init_jp_bonus(manager, building, effectiveness, log)

        cheered_up_workers = set()

        while manager.jobpoints > 0 and env.now < 105:
            yield env.timeout(5)
            simpy_debug("Entering manager_process at %s", env.now)
            # Special direct bonus to tired/sad characters
            c0 = building.cheering_up
            #c1 = not env.now % 5
            if c0 and all([
                    manager.jobpoints > 10,
                    dice(effectiveness-50)]):
                workers = [w for w in building.available_workers if
                           w != manager and
                           w not in cheered_up_workers and
                           (check_stat_perc(w, "joy", .5) or
                           check_stat_perc(w, "vitality", .3))]

                if workers:
                    worker = choice(workers)
                    cheered_up_workers.add(worker)

                    give_joy = check_stat_perc(worker, "joy", .5)
                    give_vit = check_stat_perc(worker, "vitality", .3)
                    if give_joy:
                        handle = "sad"
                    else:
                        handle = "tired"
                    temp0 = "\n{} noticed that {} looks a bit {}.".format(manager.nickname,
                                                    worker.nickname, handle)

                    if give_joy and give_vit:
                        bonus_str = "(+10% Joy, +15% Vitality)"
                        mod_by_max(worker, "joy", .1)
                        mod_by_max(worker, "vitality", .15)
                    elif give_joy:
                        bonus_str = "(+20% Joy)"
                        mod_by_max(worker, "joy", .2)
                    elif give_vit:
                        bonus_str = "(+30% Vitality)"
                        mod_by_max(worker, "vitality", .3)

                    temp1 = " Your manager cheered {} up. {}".format(worker.op,
                        set_font_color("{}".format(bonus_str), "lawngreen"))
                    log.append(temp0+temp1)

                    building.log("Your manager cheered up {}.".format(worker.name))

                    manager.jobpoints -= 10

            simpy_debug("Exiting manager_process at %s", env.now)

        # Stats:
        max_jp = manager.setAP*100
        spent_jp = max_jp - manager.jp_spent
        spent_ap = spent_jp/100.0

        exp = exp_reward(manager,
                         building.tier,
                         value=None,
                         ap_adjust=True,
                         ap_used=spent_ap,
                         char_tier_override=False,
                         final_mod=None)
        manager.logws("exp", exp)

        # TODO: Implement AP management in the function!
        stats_skills = {"management": randint(2, 4),
                        "refinement": randint(1, 2),
                        "character": randint(0, 1),
                        "intelligence": randint(1, 2)}

        temp = ss_reward(manager,
                         building.tier,
                         stats_skills,
                         ap_adjust=True,
                         ap_used=1,
                         char_tier_override=False,
                         final_mod=None,
                         apply=False)
        for s, v in temp.items():
             manager.logws(s, v)

    def mp_init_jp_bonus(manager, building, effectiveness, log):
        # Special bonus to JobPoints (aka pep talk) :D
        init_jp_bonus = (effectiveness-95.0)/100
        if init_jp_bonus < 0:
            init_jp_bonus = 0
        elif init_jp_bonus > .3: # Too much power otherwise...
            init_jp_bonus = .3
        elif init_jp_bonus < .05: # Less than 5% is absurd...
            init_jp_bonus = .05

        workers = building.available_workers
        if manager in workers:
            workers.remove(manager)

        if init_jp_bonus and workers:
            # Bonus to the maximum amount of workers:
            max_job_points = manager.jobpoints*.5
            per_worker = 10
            max_workers = round_int(max_job_points/per_worker)

            if len(workers) > max_workers:
                workers = random.sample(workers, max_workers)

            temp = "{} gave a nice motivational speech and approached some of the workers individually! ".format(manager.name)
            temp += ", ".join([w.name for w in workers])
            temp += " responded positively! "
            temp_p = "(+{}% Job Points)".format(round_int(init_jp_bonus*100))
            temp += set_font_color(temp_p, "lawngreen")
            log.append(temp)
            building.log("{} gave a motivational speech!".format(manager.name))

            init_jp_bonus += 1.0
            for w in workers:
                w.jobpoints = round_int(w.jobpoints*init_jp_bonus)
            manager.jobpoints -= len(workers)*per_worker
