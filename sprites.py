"""sprites.py – 16×16 player, 4 dirs × 2 walk frames."""
import pygame

_D0=["________________","____CCCCCC______","___CKHHHKHC_____","___CKHHHKHC_____",
     "___CKKKKKKKC____","___OKKKKKKO_____","___OKKEKKO______","___OKKKKKKO_____",
     "___OKKKKKO______","__OSSSSSSS______","_OOSSSSSSS______","__OSSSSSSS______",
     "__OPPP_PPP______","__OPPP_PPP______","__OBBB_BBB______","________________"]
_D1=["________________","____CCCCCC______","___CKHHHKHC_____","___CKHHHKHC_____",
     "___CKKKKKKKC____","___OKKKKKKO_____","___OKKEKKO______","___OKKKKKKO_____",
     "___OKKKKKO______","__OSSSSSSS______","_OOSSSSSSS______","__OSSSSSSS______",
     "_OPPPO_PPPO_____","_OPPPO_PPPO_____","_OBBBO_BBBO_____","________________"]
_U0=["________________","____CCCCCC______","___CCHHHHHCC____","___CHHHHHHHC____",
     "___CHHHHHHHC____","___OHHHHHHO_____","___OHHHHHHO_____","___OHHHHHO______",
     "__OSSSSSSS______","_OOSSSSSSS______","__OSSSSSSS______","__OPPP_PPP______",
     "__OPPP_PPP______","__OBBB_BBB______","________________","________________"]
_U1=["________________","____CCCCCC______","___CCHHHHHCC____","___CHHHHHHHC____",
     "___CHHHHHHHC____","___OHHHHHHO_____","___OHHHHHHO_____","___OHHHHHO______",
     "__OSSSSSSS______","_OOSSSSSSS______","__OSSSSSSS______","_OPPPO_PPPO_____",
     "_OPPPO_PPPO_____","_OBBBO_BBBO_____","________________","________________"]
_L0=["________________","___CCCCCC_______","__CKHHHKC_______","__CKHHHKC_______",
     "__CKKKKKKC______","_OKKKKKKK_______","_OKKE_KKK_______","_OKKKKKKK_______",
     "_OKKKKKK________","OSSSSSSS________","OSSSSSSS________","OSSSSSSS________",
     "_OPPPPP_________","_OPPPPP_________","__OBBBBB________","___OBBBB________"]
_L1=["________________","___CCCCCC_______","__CKHHHKC_______","__CKHHHKC_______",
     "__CKKKKKKC______","_OKKKKKKK_______","_OKKE_KKK_______","_OKKKKKKK_______",
     "_OKKKKKK________","OSSSSSSS________","OSSSSSSS________","OSSSSSSS________",
     "__OPPPP_________","__OPPPP_________","___OBBB_________","____OBB_________"]

_P={'K':(255,210,168),'H':(55,28,8),'C':(210,40,40),'S':(50,115,215),
    'P':(32,32,105),'B':(22,15,6),'O':(8,8,8),'E':(0,0,0),'_':None}

def _mk(t):
    s=pygame.Surface((16,16),pygame.SRCALPHA); s.fill((0,0,0,0))
    for r,row in enumerate(t):
        for c,ch in enumerate(row[:16]):
            col=_P.get(ch)
            if col: s.set_at((c,r),(*col,255))
    return s

def create_player_sprites():
    l0=_mk(_L0);l1=_mk(_L1)
    r0=pygame.transform.flip(l0,True,False);r1=pygame.transform.flip(l1,True,False)
    d0=_mk(_D0);d1=_mk(_D1);u0=_mk(_U0);u1=_mk(_U1)
    return{(0,0):l0,(0,1):l1,(1,0):r0,(1,1):r1,(2,0):d0,(2,1):d1,(3,0):u0,(3,1):u1}