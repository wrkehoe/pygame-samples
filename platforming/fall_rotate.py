"""This is identical tp fall_mask.py except that the sprite spins when moving
while contacting the ground. Just for fun."""
import os,sys
from random import randint
import pygame as pg

class _Physics:
    def __init__(self):
        self.x_vel = self.y_vel = self.y_vel_i = 0
        self.grav = 20
        self.fall = False
        self.time = None
    def phys_update(self):
        if self.fall:
            if not self.time:
                self.time = pg.time.get_ticks()
            self.y_vel = self.grav*((pg.time.get_ticks()-self.time)/1000.0) + self.y_vel_i
        else:
            self.time = None
            self.y_vel = 0

class Player(_Physics):
    """Class representing our player."""
    def __init__(self, location,speed):
        _Physics.__init__(self)
        self.angle = 0
        self.rect = BASEFACE.get_rect(topleft=location)
        self.orig_image = self.make_image()
        self.image = self.orig_image.copy()
        self.mask  = pg.mask.from_surface(BASEFACE)
        self.speed = speed
        self.jump_power = 10

    def get_pos(self,Mask):
        """Calculate where our player will end up this frame including collissions."""
        #Has the player walked off an edge?
        if not self.fall and not self.simple_overlap(Mask,[0,1]):
            self.fall = True
        #Has the player landed from a fall or jumped into an object above them?
        elif self.fall and self.simple_overlap(Mask,[0,int(self.y_vel)]):
            self.y_vel = self.adjust_pos(Mask,[0,int(self.y_vel)],1)
            self.y_vel_i = 0
            self.fall = False
        self.rect.y += int(self.y_vel) #Update y position before testing x.
        #Is the player running into a wall?.
        if self.simple_overlap(Mask,(int(self.x_vel),0)):
            self.x_vel = self.adjust_pos(Mask,[int(self.x_vel),0],0)
        self.rect.x += int(self.x_vel)
    def adjust_pos(self,Mask,offset,off_ind):
        while self.simple_overlap(Mask,offset):
            offset[off_ind] += (1 if offset[off_ind]<0 else -1)
        return offset[off_ind]
    def simple_overlap(self,Mask,offset):
        off = (self.rect.x+offset[0],self.rect.y+offset[1])
        return Mask.overlap_area(self.mask,off)

    def update(self,Surf,Mask):
        self.get_pos(Mask)
        self.phys_update()
        self.image = self.make_image()
        blit_rect = self.image.get_rect(center=self.rect.center)
        Surf.blit(self.image,blit_rect)

    def make_image(self):
        temp = pg.Surface((self.rect.size)).convert_alpha()
        temp.fill((0,0,0,0))
        temp.blit(BASEFACE,(0,0))
        face = pg.transform.rotozoom(FACE,self.angle,1)
        face_rect = face.get_rect(center=temp.get_rect().center)
        temp.blit(face,face_rect)
        return temp

class Block:
    """Class representing obstacles."""
    def __init__(self,location):
        self.make_image()
        self.rect = pg.Rect(location,(50,50))
    def make_image(self):
        self.image = pg.Surface((50,50)).convert_alpha()
        self.image.fill([randint(0,255) for i in range(3)])
        self.image.blit(SHADE_IMG,(0,0))
    def update(self,Surf):
        Surf.blit(self.image,self.rect)

class Control:
    """Class for managing event loop and game states."""
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.state = "GAME"
        self.Player = Player((50,-25), 4)
        self.make_obstacles()
        self.bg_mask,self.bg_image = self.make_bg_mask()
        self.Clock = pg.time.Clock()
    def event_loop(self):
        keys = pg.key.get_pressed()
        self.Player.x_vel = 0
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.Player.x_vel -= self.Player.speed
            if not self.Player.fall:
                self.Player.angle += self.Player.speed
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.Player.x_vel += self.Player.speed
            if not self.Player.fall:
                self.Player.angle -= self.Player.speed
        for event in pg.event.get():
            if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                self.state = "QUIT"
            elif event.type == pg.KEYDOWN: #Key down events.
                if event.key == pg.K_SPACE and not self.Player.fall: #Jump
                    self.Player.y_vel_i = -self.Player.jump_power
                    self.Player.fall = True

    def update(self):
        self.screen.fill((50,50,50))
        self.screen.blit(self.bg_image,(0,0))
        self.Player.update(self.screen,self.bg_mask)
    def main(self):
        """Our games infinite loop"""
        while True:
            if self.state == "GAME":
                self.event_loop()
                self.update()
            elif self.state == "QUIT":
                break
            pg.display.update()
            self.Clock.tick(65)
    def make_obstacles(self):
        self.Obstacles = [Block((400,400)),Block((300,270)),Block((150,170))]
        self.Obstacles += [Block((500+50*i,220)) for i in range(3)]
        for i in range(12):
            self.Obstacles.append(Block((50+i*50,450)))
            self.Obstacles.append(Block((100+i*50,0)))
            self.Obstacles.append(Block((0,50*i)))
            self.Obstacles.append(Block((650,50*i)))
    def make_bg_mask(self):
        temp = pg.Surface(SCREENSIZE).convert_alpha()
        temp.fill((0,0,0,0))
        for obs in self.Obstacles:
            obs.update(temp)
        return pg.mask.from_surface(temp),temp

#####################
if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    SCREENSIZE = (700,500)
    pg.display.set_mode(SCREENSIZE)
    BASEFACE = pg.image.load("base_face.png").convert_alpha()
    FACE  = pg.image.load("just_face.png").convert_alpha()
    SHADE_IMG = pg.image.load("shader.png").convert_alpha()

    RunIt = Control()
    RunIt.main()
    pg.quit();sys.exit()