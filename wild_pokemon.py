from pokemon import Pokemon
from move import Move
import random
tackle=Move("Tackle",8,"normal");quick=Move("Quick Attack",9,"normal");bite=Move("Bite",10,"normal");scratch=Move("Scratch",9,"normal")
leaf_cut=Move("Leaf Cut",10,"grass");vine=Move("Vine Whip",12,"grass");razor=Move("Razor Leaf",13,"grass");petal=Move("Petal Dance",14,"grass")
ember=Move("Ember",10,"fire");flare=Move("Flame Burst",12,"fire");ffang=Move("Fire Fang",13,"fire");heat=Move("Heat Wave",14,"fire")
wgun=Move("Water Gun",10,"water");bubble=Move("Bubble Beam",12,"water");aqua=Move("Aqua Tail",13,"water");hydro=Move("Hydro Pump",15,"water")
tshock=Move("ThunderShock",11,"electric");spark=Move("Spark",13,"electric");volt=Move("Volt Tackle",15,"electric");twave=Move("Thunder Wave",10,"electric")
conf=Move("Confusion",11,"psychic");psyb=Move("Psybeam",13,"psychic");psych=Move("Psychic",15,"psychic");fsight=Move("Future Sight",14,"psychic")
rthrow=Move("Rock Throw",11,"rock");rslide=Move("Rock Slide",13,"rock");sedge=Move("Stone Edge",15,"rock");rollout=Move("Rollout",10,"rock")
lick=Move("Lick",10,"ghost");sball=Move("Shadow Ball",14,"ghost");hexm=Move("Hex",13,"ghost");nshade=Move("Night Shade",12,"ghost")
_POOL=[
    Pokemon("Sprout","grass",34,[leaf_cut,tackle,vine,quick],(80,200,70)),
    Pokemon("Budroo","grass",38,[vine,tackle,razor,bite],(55,175,65)),
    Pokemon("Fernix","grass",44,[razor,petal,leaf_cut,quick],(40,150,55)),
    Pokemon("Flarecub","fire",34,[ember,tackle,flare,quick],(255,130,70)),
    Pokemon("Cinderpup","fire",38,[flare,tackle,ember,bite],(240,90,50)),
    Pokemon("Magmite","fire",44,[ffang,heat,ember,quick],(200,50,20)),
    Pokemon("Bubbletoad","water",34,[wgun,tackle,bubble,quick],(70,160,255)),
    Pokemon("Aqualy","water",38,[bubble,tackle,wgun,bite],(45,140,235)),
    Pokemon("Finwave","water",44,[aqua,hydro,wgun,quick],(30,110,210)),
    Pokemon("Zappi","electric",34,[tshock,tackle,spark,quick],(255,230,40)),
    Pokemon("Voltpup","electric",38,[spark,tackle,twave,bite],(230,200,30)),
    Pokemon("Boltfox","electric",44,[volt,tshock,spark,quick],(200,170,20)),
    Pokemon("Drowsi","psychic",34,[conf,tackle,psyb,quick],(200,120,230)),
    Pokemon("Mindril","psychic",38,[psyb,tackle,conf,scratch],(180,90,210)),
    Pokemon("Abyssal","psychic",44,[psych,fsight,psyb,conf],(150,60,190)),
    Pokemon("Pebblite","rock",34,[rthrow,tackle,rollout,scratch],(160,140,110)),
    Pokemon("Granyte","rock",38,[rslide,tackle,rthrow,bite],(130,110,85)),
    Pokemon("Bouldrix","rock",44,[sedge,rslide,rthrow,quick],(100,85,65)),
    Pokemon("Spooklet","ghost",34,[lick,tackle,nshade,scratch],(120,80,160)),
    Pokemon("Wraithon","ghost",38,[sball,lick,hexm,bite],(90,55,130)),
    Pokemon("Phantera","ghost",44,[hexm,sball,lick,nshade],(65,35,100)),
]
_BY={};
for _p in _POOL: _BY.setdefault(_p.type,[]).append(_p)
_T=list(_BY.keys())
def random_wild(): return random.choice(_BY[random.choice(_T)]).clone()
wild=_POOL