from pokemon import Pokemon
from move import Move

tackle = Move("Tackle", 8, "normal")
quick_attack = Move("Quick Attack", 9, "normal")

ember = Move("Ember", 11, "fire")
flame_burst = Move("Flame Burst", 13, "fire")

water_gun = Move("Water Gun", 11, "water")
bubble_beam = Move("Bubble Beam", 13, "water")

leaf_cut = Move("Leaf Cut", 11, "grass")
vine_whip = Move("Vine Whip", 13, "grass")

starters = [
    Pokemon(
        "Flamio",
        "fire",
        52,
        [ember, tackle, flame_burst, quick_attack],
        (255, 110, 50),
    ),
    Pokemon(
        "Aquava",
        "water",
        55,
        [water_gun, tackle, bubble_beam, quick_attack],
        (50, 140, 255),
    ),
    Pokemon(
        "Leafy",
        "grass",
        58,
        [leaf_cut, tackle, vine_whip, quick_attack],
        (60, 220, 80),
    ),
]