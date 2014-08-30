# TODO: Fix bug where bullet spwns in wall and causes index error
#       Make everything able to use the portals again



from random import choice

import pygame
from pygame.locals import *

# i'm gonna try to make a thing where you fight enemies in a room that come out of the walls

ZONE_SIZE = 21
ZONE = []
for y in range(ZONE_SIZE): #this will build the playmap using the size
    ZONE.append([])
    for x in range(ZONE_SIZE):
        if y == 0 or y == (ZONE_SIZE-1):
            if x == (ZONE_SIZE-1)/2:
                ZONE[y].append(2)
            else:
                ZONE[y].append(1)
        else:
            if x == 0 or x == (ZONE_SIZE-1):
                if y == (ZONE_SIZE-1)/2:
                    ZONE[y].append(2)
                else:
                    ZONE[y].append(1)
            else:
                ZONE[y].append(0)
#note that due to the way whole division works this map creation code
#will only work on an odd map size

PLAY_AREA = ((len(ZONE)*32)+34, len(ZONE)*32) #the screen size assumes ZONE
                                         #is a square map

#initialization
pygame.init()
#main window
screen = pygame.display.set_mode(PLAY_AREA, DOUBLEBUF)
#Clock object
clock = pygame.time.Clock()

#engine objects and functions
class Imager: #use this interface to load and use images
    def __init__(self):
        self.images = {}

    def load(self, name, image):
        if not (image in self.images):
            self.images[name] = pygame.image.load(image)
            return self.images[name]
        else:
            return self.images[name]

    def use(self, name):
        if name in self.images:
            return self.images[name]
        else:
            print "image not loaded"
            return None
            
def render_all():
    global screen
    global ZONE
    global player
    global monsters
    global bullets
    global PLAY_AREA
    global imager
    
    # this function assumes ZONE is a square map
    screen.fill((0,0,0)) #erase before redrawing playing field

    for y in range(len(ZONE)):
        for x in range(len(ZONE)):
            if ZONE[y][x] == 1 or ZONE[y][x] == 2:
                drawx = x*32 #this are the base coordinates to work from
                drawy = y*32 #when drawing
                rect = pygame.Rect(drawx, drawy, 32, 32)
                pygame.draw.rect(screen, (255,255,255), rect)
                rect = pygame.Rect(drawx+1, drawy+1, 30, 30)
                pygame.draw.rect(screen, (30,30,30), rect)
                #the four lines above will draw a grey square
                #with a white border
            if ZONE[y][x] == 2:
                #for the portal we'll just draw the same but with a circle inside
                drawx = x*32 #this are the base coordinates to work from
                drawy = y*32 #when drawing
                rect = pygame.Rect(drawx, drawy, 32, 32)
                pygame.draw.circle(screen, (0,0,255), rect.center, 15)

    #draw monsters
    for mob in monsters:
        drawx = mob.posx*32
        drawy = mob.posy*32
        rect = pygame.Rect(drawx, drawy, 32, 32)
        pygame.draw.circle(screen, (255,0,0), rect.center, 15)

    #draw bullets
    for bullet in bullets:
        drawx = bullet.posx*32
        drawy = bullet.posy*32
        rect = pygame.Rect(drawx, drawy, 32, 32)
        pygame.draw.circle(screen, (200,200,200), rect.center, 2)

    #draw the player
    drawx = player.posx*32
    drawy = player.posy*32
    rect = pygame.Rect(drawx, drawy, 32, 32)
    pygame.draw.circle(screen, (0,255,0), rect.center, 15)

    #draw health bar
    for i in range(player.health):
        drawx = PLAY_AREA[0]-33
        drawy = 1+(i*32)
        screen.blit(imager.use("health"), (drawx, drawy))
        
    

#game objects and functions
class Actor:
    
    def __init__(self):
        self.posx = 0
        self.posy = 0
        self.facing = "S"

    def up(self):
        global ZONE
        
        if ZONE[self.posy-1][self.posx] == 0:
            self.posy -= 1
            self.facing = "N"
            return False
        else:
            return True
            
    def down(self):
        global ZONE
        
        if ZONE[self.posy+1][self.posx] == 0:
            self.posy += 1
            self.facing = "S"
            return False
        else:
            return True
            
    def left(self):
        global ZONE
        
        if ZONE[self.posy][self.posx-1] == 0:
            self.posx -= 1
            self.facing = "W"
            return False
        else:
            return True
            
    def right(self):
        global ZONE
        
        if ZONE[self.posy][self.posx+1] == 0:
            self.posx += 1
            self.facing = "E"
            return False
        else:
            return True

    
class Player(Actor):
    
    def __init__(self):
        self.health = 10
        self.posx = ZONE_SIZE/2
        self.posy = ZONE_SIZE/2
        self.loadtime = 0
        self.loaded = True

    def update(self):
        if self.loadtime > 0:
            self.loadtime -= 1
        else:
            self.loaded = True

    def shoot(self):
        bullets.append(Shot(self.facing))
        self.loaded = False
        self.loadtime = 10

class Shot(Actor):

    def __init__(self, facing):
        global player
        self.timer = 0
        
        if facing == "N":
            self.dir = self.up
            self.posx = player.posx
            self.posy = player.posy-1
        elif facing == "S":
            self.dir = self.down
            self.posx = player.posx
            self.posy = player.posy+1
        elif facing == "W":
            self.dir = self.left
            self.posx = player.posx-1
            self.posy = player.posy
        elif facing == "E":
            self.dir = self.right
            self.posx = player.posx+1
            self.posy = player.posy

    def update(self):
        global monsters
        global bullets
        
        if self.timer == 0:
            self.timer = 1
            if self.dir():
                bullets.remove(self)
        else:
            self.timer -= 1

        for mob in monsters:
            if self.posx == mob.posx and self.posy == mob.posy:
                mob.damage(1)
                bullets.remove(self)
    
    

class Wanderer(Actor):
    
    def __init__(self, pos):
        self.health = 1
        self.posx = pos[0]
        self.posy = pos[1]
        self.timer = 0

    def damage(self, n):
        self.health -= n

    def update(self):
        global player
        global monsters
        
        move = [self.up, self.down, self.left, self.right]
        self.timer += 1
        if self.timer >= 5:
            choice(move)()
            self.timer = 0
        if self.posx == player.posx and self.posy == player.posy:
            player.health -= 1
            self.damage(1)

        #die if health is zero - I should eventually make a base monster
        if self.health <= 0:
            monsters.remove(self)

#initialize objects
imager = Imager()
            
player = Player() #initialize a player object
imager.load("health", "health.png") #load the health sprite

monsters = []
for i in range(10):
    portalx = ZONE_SIZE/2
    portaly = ZONE_SIZE/2
    portals = [(1, portaly), (ZONE_SIZE-2, portaly),
               (portalx, 1), (portalx, ZONE_SIZE-2)]
    monsters.append(Wanderer(choice(portals)))
    
bullets = []

paused = True #start the game paused

# main game loop - still very basic
while True:
    stop = False
    clock.tick(25)

    render_all()
    
    for event in pygame.event.get():
        #check for exit events
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            stop = True
        elif event.type == QUIT:
            stop = True

        #check for pause key
        if event.type == KEYDOWN and event.key == K_p:
            paused = (not paused) #reverse the pause state when detected
            
        if not paused:
            #check for player events
            #movement keys
            if event.type == KEYDOWN:
                if event.key == K_UP or event.key == K_w:
                    player.up()
                    player.facing = "N"
                elif event.key == K_DOWN or event.key == K_s:
                    player.down()
                    player.facing = "S"
                elif event.key == K_LEFT or event.key == K_a:
                    player.left()
                    player.facing = "W"
                elif event.key == K_RIGHT or event.key == K_d:
                    player.right()
                    player.facing = "E"
            #shooting key
            if event.type == KEYDOWN and event.key == K_SPACE:
                if player.loaded:
                    player.shoot()
                    
    #tick player, for weapon timer
    if not paused:
        player.update()

    if not paused:
        #update mobs
        for mob in monsters:
            mob.update()
        #then update bullets, giving mobs a chance to dodge
        for bullet in bullets:
            bullet.update()
            

    pygame.display.update()
    if stop == True:
        print "successful quit"
        pygame.quit()
        break
