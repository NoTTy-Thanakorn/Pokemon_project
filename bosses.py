from pokemon import Pokemon
from move import Move
slam=Move("Titan Slam",14,"normal");ancient=Move("Ancient Force",16,"normal")
inferno=Move("Inferno",20,"fire");lava=Move("Lava Burst",22,"fire");heat=Move("Heat Wave",18,"fire")
tsunami=Move("Tsunami",20,"water");aquaruin=Move("Aqua Ruin",22,"water");hydro=Move("Hydro Cannon",24,"water")
nature=Move("Nature Wrath",20,"grass");forest=Move("Forest Crush",22,"grass");petal=Move("Petal Blizzard",18,"grass")
thunder=Move("Thunder",22,"electric");volt=Move("Volt Crash",24,"electric");discharge=Move("Discharge",18,"electric")
sforce=Move("Shadow Force",24,"ghost");prage=Move("Phantom Rage",22,"ghost");dpulse=Move("Dark Pulse",20,"ghost")
bosses=[
    Pokemon("VolcanoDrake","fire",140,[lava,inferno,heat,ancient],(255,55,20)),
    Pokemon("OceanTitan","water",145,[hydro,tsunami,aquaruin,ancient],(30,120,255)),
    Pokemon("ForestAncient","grass",148,[petal,forest,nature,ancient],(35,195,85)),
    Pokemon("ThunderGod","electric",142,[volt,thunder,discharge,ancient],(255,235,30)),
    Pokemon("ShadowWraith","ghost",150,[sforce,prage,dpulse,ancient],(80,40,130)),
]