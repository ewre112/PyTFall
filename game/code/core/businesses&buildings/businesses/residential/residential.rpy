init -6 python:
    # Provides living space, not sure if this or the building should be bound as home locations!
    class SlaveQuarters(Business):
        SORTING_ORDER = 0
        def __init__(self, name="Slave Quarters", instance=None,
                     desc="Place for slaves to live in!",
                     img="content/buildings/upgrades/guard_qt.jpg",
                     build_effort=0, materials=None, in_slots=2, ex_slots=0,
                     cost=500, **kwargs):
            super(SlaveQuarters, self).__init__(name=name, instance=instance,
                  desc=desc, img=img, build_effort=build_effort,
                  materials=materials, cost=cost, **kwargs)
            # self.rooms = in_slots
