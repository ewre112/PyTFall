label hiddenvillage_entrance:
    $ gm.enter_location(limited_location=True)
    $ coords = [[.2, .25], [.55, .2], [.8, .18]]
    if not "village" in ilists.world_music:
        $ ilists.world_music["village"] = [track for track in os.listdir(content_path("sfx/music/world")) if track.startswith("village")]
    if not global_flags.has_flag("keep_playing_music"):
        play world choice(ilists.world_music["village"]) fadein .5
    $ global_flags.del_flag("keep_playing_music")

    python:
        # Build the actions
        if pytfall.world_actions.location("hiddenvillage_entrance"):
            pytfall.world_actions.meet_girls()
            pytfall.world_actions.look_around()
            pytfall.world_actions.finish()

    if global_flags.flag('visited_hidden_village'): # should be changed to not global_flags.flag('visited_hidden_village') before the release !!!!!!!!!!!!!!!!!!!
        $ global_flags.set_flag('visited_hidden_village')

    scene bg hiddenvillage_entrance
    show screen hiddenvillage_entrance

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    while True:

        $ result = ui.interact()

        if result[0] == 'jump':
            $ gm.start_gm(result[1], img=result[1].show("girlmeets", "suburb", exclude=["beach", "winter", "night", "formal", "indoors", "swimsuit"], type="first_default", label_cache=True, resize=I_IMAGE_SIZE, gm_mode=True))

        if result[0] == 'control':
            hide screen hiddenvillage_entrance
            if result[1] == 'return':
                $ renpy.music.stop(channel="world")
                hide screen hiddenvillage_entrance
                jump city


screen hiddenvillage_entrance:

    use top_stripe(True)

    use location_actions("hiddenvillage_entrance")
    if not gm.show_girls:
        $img = ProportionalScale("content/gfx/interface/icons/ninja_shop.png", 100, 70)
        imagebutton:
            pos(300, 315)
            idle (img)
            hover (im.MatrixColor(img, im.matrix.brightness(.15)))
            action [Hide("hiddenvillage_entrance"), Jump("hidden_village_shop")]
            tooltip "Ninja Shop"

    if gm.show_girls:
        key "mousedown_3" action ToggleField(gm, "show_girls")

        add "content/gfx/images/bg_gradient.webp" yalign .45

        for j, entry in enumerate(gm.display_girls()):
            hbox:
                align (coords[j])
                use rg_lightbutton(return_value=['jump', entry])

label hidden_village_shop: # ninja shop logic
    if not "shops" in ilists.world_music:
        $ ilists.world_music["shops"] = [track for track in os.listdir(content_path("sfx/music/world")) if track.startswith("shops")]
    if not global_flags.has_flag("keep_playing_music"):
        play world choice(ilists.world_music["shops"]) fadein 1.5

    hide bg hiddenvillage_entrance

    scene bg workshop
    with dissolve
    show expression npcs["Ren_hidden_village"].get_vnsprite() as ren
    with dissolve
    $ hidden_village_shop = ItemShop("Ninja Tools Shop", 18, ["Ninja Shop"], gold=1000, sells=["armor", "dagger", "fists", "rod", "claws", "sword", "bow", "amulet", "smallweapon", "restore", "dress"], sell_margin=.85, buy_margin=3.0)
    $ r = npcs["Ren_hidden_village"].say

    if global_flags.flag('hidden_village_shop_first_enter'):
        r "Hey, [hero.name]. Need something?"
    else:
        $ r = Character("???", color=red, what_color=orange, show_two_window=True)
        $ global_flags.set_flag('hidden_village_shop_first_enter')
        r "Hm? Ah, I've heard about you."
        extend " Welcome to my Tools Shop."
        $ r = npcs["Ren_hidden_village"].say
        r "I'm Ren. We sell ninja stuff here."
        r "If we are interested, I can sell you some leftovers. Of course, it won't be cheap for an outsider like you."
        r "But you won't find these things anywhere else, so it is worth it."
        r "Wanna take a look?"
    python:
        focus = False
        item_price = 0
        filter = "all"
        amount = 1
        shop = pytfall.hidden_village_shop
        shop.inventory.apply_filter(filter)
        char = hero
        char.inventory.set_page_size(18)
        char.inventory.apply_filter(filter)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve
    $ pytfall.world_events.run_events("auto")

    call shop_control from _call_shop_control_5

    $ global_flags.del_flag("keep_playing_music")
    hide screen shopping
    with dissolve
    jump hiddenvillage_entrance
