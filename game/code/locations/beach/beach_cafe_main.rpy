label city_beach_cafe_main:
    $ gm.enter_location(goodtraits=["Athletic", "Dawdler", "Always Hungry"], badtraits=["Scars", "Undead", "Furry", "Monster"], curious_priority=False)
    $ coords = [[.15, .75], [.5, .6], [.9, .8]]
    # Music related:
    if not "beach_cafe" in ilists.world_music:
        $ ilists.world_music["beach_cafe"] = [track for track in os.listdir(content_path("sfx/music/world")) if track.startswith("beach_cafe")]
    if not global_flags.has_flag("keep_playing_music"):
        play world choice(ilists.world_music["beach_cafe"])
    $ global_flags.del_flag("keep_playing_music")

    python:
        # Build the actions
        if pytfall.world_actions.location("city_beach_cafe_main"):
            pytfall.world_actions.meet_girls()
            pytfall.world_actions.look_around()
            pytfall.world_actions.finish()

    scene bg city_beach_cafe_main
    with dissolve
    show screen city_beach_cafe_main

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    while 1:

        $ result = ui.interact()

        if result[0] == 'jump':
            $ girl = result[1]
            $ tags = girl.get_tags_from_cache(last_label)
            if not tags:
                $ img_tags = (["girlmeets", "beach"], ["girlmeets", "swimsuit", "simple bg"], ["girlmeets", "swimsuit", "no bg"], ["girlmeets", "swimsuit", "outdoors"])
                $ result = get_simple_act(girl, img_tags)
                if not result:
                    $ img_tags = (["girlmeets", "simple bg"], ["girlmeets", "no bg"])
                    $ result = get_simple_act(girl, img_tags)
                    if not result:
                        # giveup
                        $ result = ("girlmeets", "swimsuit")
                $ tags.extend(result)

            $ gm.start_gm(girl, img=girl.show(*tags, type="reduce", label_cache=True, resize=I_IMAGE_SIZE, gm_mode=True))

        if result[0] == 'control':
            if result[1] == 'return':
                hide screen city_beach_cafe_main
                jump city_beach_left


screen city_beach_cafe_main:

    use top_stripe(True)
    if not gm.show_girls:
        # Jump buttons:
        $ img = im.Flip(im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80), horizontal=True)
        imagebutton:
            align (.01, .5)
            idle (img)
            hover (im.MatrixColor(img, im.matrix.brightness(.15)))
            action [Hide("city_beach_cafe_main"), Function(global_flags.del_flag, "keep_playing_music"), Jump("city_beach_cafe")]

        $img = im.Scale(im.Flip("content/gfx/interface/buttons/blue_arrow_up.png", vertical=True), 80, 70)
        imagebutton:
            align (.5, .99)
            idle (img)
            hover (im.MatrixColor(img, im.matrix.brightness(.15)))
            action [Hide("city_beach_cafe_main"), Jump("city_beach_left")]

    use location_actions("city_beach_cafe_main")

    if gm.show_girls:
        key "mousedown_3" action ToggleField(gm, "show_girls")

        add "content/gfx/images/bg_gradient.webp" yalign .45

        for j, entry in enumerate(gm.display_girls()):
            hbox:
                align (coords[j])
                use rg_lightbutton(return_value=['jump', entry])
