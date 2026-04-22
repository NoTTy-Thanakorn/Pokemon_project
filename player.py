"""player.py – moves validated by main.py via is_walkable()."""
import pygame
from sprites import create_player_sprites

class Player:
    def __init__(self):
        self.x=1; self.y=1
        self.dir=1; self.step=0; self.frame=0
        self.sprites=create_player_sprites()
        self.steps_total=0

    def move(self,dx,dy):
        """Called only when destination already confirmed walkable."""
        self.x+=dx; self.y+=dy
        self.step+=1; self.frame=(self.step//2)%2
        self.steps_total+=1
        if dx>0: self.dir=1
        elif dx<0: self.dir=0
        elif dy>0: self.dir=2
        elif dy<0: self.dir=3

    def draw(self,screen,tile):
        img=pygame.transform.scale(self.sprites[(self.dir,self.frame)],(tile,tile))
        screen.blit(img,(self.x*tile,self.y*tile))