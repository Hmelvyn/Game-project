import os
import random
import pygame
import math
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000, 600
FPS = 50
PLAYER_VEL = 5

left_boundary = -2525
right_boundary = 2925
stop_scroll_l = -1835
stop_scroll_r = 2715



window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))] #lists every file name in that dir

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
        
    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)



class Player(pygame.sprite.Sprite):
    COLOUR = (255,0,0)
    GFORCE = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_LAG = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.how_long_falling = 0
        self.jump_count = 0
        self.hit = False
        self.hit_time = 0
    
    def jump(self):
        self.y_vel = -self.GFORCE * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.how_long_falling = 0
    
    def move(self, dx, dy):        
        self.rect.x += dx
        self.rect.y += dy

    def got_hit(self):
        self.hit = True
        self.hit_time = 0


    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.how_long_falling / fps) * self.GFORCE)
        self.move(self.x_vel, self.y_vel)
        if self.hit:
            self.hit_time += 1
        if self.hit_time > fps * 2:
            self.hit = False

        self.how_long_falling += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
    
    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GFORCE * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_LAG) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()


    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
    
    def draw(self, win, offset_x):       
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
    
    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Saw(Object):
    ANIMATION_LAG = 3


    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "saw")
        self.saw = load_sprite_sheets("Traps", "Saw", width, height)
        self.image = self.saw["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off" 
    
    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"
    
    def loop(self):    
        sprites = self.saw[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_LAG) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_LAG > len(sprites):
            self.animation_count = 0



def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height, = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = [i * width, j * height]
            tiles.append(pos)

    return tiles, image
        
def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)
    
    player.draw(window, offset_x)

    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if obj.name == "saw":
                # Determine collision direction
                if dy > 0:
                    # Player is falling onto the saw
                    player.rect.bottom = obj.rect.top  # Place player above the saw
                    player.y_vel = -player.GFORCE * 5  # Simulate a bounce upwards
                elif dy < 0:
                    # Player is hitting the saw from below (unlikely for saw, but for completeness)
                    player.rect.top = obj.rect.bottom  # Move player below the saw
                    player.y_vel = player.GFORCE * 5  # Simulate a bounce downwards
                
                # Horizontal bounce (optional, adjust as needed)
                if player.rect.centerx < obj.rect.centerx:
                    # Player is on the left of the saw
                    player.rect.right = obj.rect.left  # Move player to the left of the saw
                    player.x_vel = -PLAYER_VEL  # Simulate a bounce to the left
                else:
                    # Player is on the right of the saw
                      # Move player to the right of the saw
                    player.x_vel = PLAYER_VEL  # Simulate a bounce to the right

            else:
                # Handle normal collision with other objects
                if dy > 0:
                    player.rect.bottom = obj.rect.top  # Place player above the object
                    player.landed()  # Reset jump count, stop falling
                elif dy < 0:
                    player.rect.top = obj.rect.bottom  # Move player below the object
                    player.hit_head()  # Reverse vertical velocity
     

                collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx, dy):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    
    player.move(-dx, 0)
    player.update()
    return collided_object



def handle_move(player, objects):


    keys = pygame.key.get_pressed()

    player.x_vel = 0
    handle_vertical_collision(player, objects, player.y_vel)
    collide_left = collide(player, objects, -PLAYER_VEL, player.y_vel * 2)
    collide_right = collide(player, objects, PLAYER_VEL, player.y_vel * 2)
 
    if keys[pygame.K_LEFT] and not collide_left:
        if player.rect.x > left_boundary:  #controls boundary on left
            player.move_left(PLAYER_VEL) 
            
    if keys[pygame.K_RIGHT] and not collide_right:
        if player.rect.x < right_boundary: #controls boundary on right
            player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    check_obj = [collide_left, collide_right, *vertical_collide] # * for vertical collide looks through all objects
    for obj in check_obj:
        if obj and obj.name == 'saw':
            player.got_hit()
           
                

    if player.rect.top < 0:  # Top boundary check
        player.rect.top = 0
        player.y_vel = 0

    # handle_vertical_collision(player, objects, player.y_vel)


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Pink.png")
    
    #objects
    up_1_saw = (38 * 2)
    block_size = 96


    player = Player(35, 344, 50, 50)
    saw1 = Saw(500, HEIGHT - block_size - up_1_saw, 38, 38)    #may need to adjust size
    saw2 = Saw(500, HEIGHT - block_size - up_1_saw * 2, 38, 38)
    saw3 = Saw(500, HEIGHT - block_size - up_1_saw * 5, 38, 38)
    saw4 = Saw(500, HEIGHT - block_size - up_1_saw * 6, 38, 38)
    saw1.on()
    saw2.on()
    saw3.on()
    saw4.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) 
             for i in range (-(WIDTH * 2) // block_size, (WIDTH * 3) // block_size)]
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size), Block(1500, 344, block_size), Block(1800, 144, block_size), saw1, saw2, saw3, saw4]
    starting_pos = (player.rect.x - 50)

    offset_x = (starting_pos) #gives the ideal starting position
    scroll_area_width = 200 #210 in reality, 10 possible transparent pixel

    print_counter = 0

   



    run = True
    while run:
        clock.tick(FPS)
        
        print_counter += 1
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
                    

        player.loop(FPS)
        saw1.loop()
        saw2.loop()
        saw3.loop()
        saw4.loop()
        handle_move(player, objects)
       
        draw(window, background, bg_image, player, objects, offset_x)

        edge_distance_r = player.rect.right - offset_x
        dist_from_scroll_r = WIDTH - scroll_area_width
        edge_distance_l = player.rect.left - offset_x

        if player.rect.y > 600:
            print("Dead")


        if print_counter == 80:
            print(edge_distance_r, dist_from_scroll_r, edge_distance_l, scroll_area_width)
            print(player.rect.x, player.rect.y)
            print(stop_scroll_l)
            print_counter = 0

        
        if player.rect.x > stop_scroll_l and player.rect.x < stop_scroll_r:
            if ((edge_distance_r >= dist_from_scroll_r) and player.x_vel > 0) or ((edge_distance_l <= scroll_area_width) and player.x_vel < 0):
                offset_x += player.x_vel
         
        

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)
