from pokemon_sprite import create_mon_sprite
class Pokemon:
    def __init__(self,name,ptype,hp,moves,color):
        self.name=name;self.type=ptype;self.max_hp=hp;self.hp=hp
        self.moves=moves;self.color=color;self.sprite=create_mon_sprite(color,ptype,32)
    def reset(self): self.hp=self.max_hp
    def is_fainted(self): return self.hp<=0
    def clone(self): return Pokemon(self.name,self.type,self.max_hp,self.moves[:],self.color)