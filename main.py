import pygame
import time
import os
import random
import neat

pygame.font.init()

# __ = dunder
# __init__ = dunder init

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 700

BIRD_X = 150

DIR_ASSETS = "assets"

def get_image(file):
    return  pygame.image.load(os.path.join(DIR_ASSETS, file))
def scale_image(file, scale):
    img = get_image(file)
    width = round(img.get_width()*scale)
    height = round(img.get_height()*scale)
    return pygame.transform.scale(img, (width, height)) 

BIRD_IMGS = [scale_image("bird1.png", 1.5),
             scale_image("bird2.png", 1.5),
             scale_image("bird3.png", 1.5)]
PIPE_IMG = scale_image("pipe.png", 1.5)
BASE_IMG = get_image("base.png")
BASE_IMG = pygame.transform.scale(BASE_IMG, (round(BASE_IMG.get_width()*1.5), 200))
BACKGROUND_iMG = get_image("bg.png")
BACKGROUND_iMG = pygame.transform.scale(BACKGROUND_iMG, (SCREEN_WIDTH, SCREEN_HEIGHT))

STAT_FONT = pygame.font.SysFont("comicsans", 40)

class Bird():
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y
    
    def move(self):
        self.tick_count += 1

        # d = v*t + t*v^2
        d =  self.vel * self.tick_count + 1.5 * self.tick_count ** 2 

        # Apply terminal velocity
        if d >= 16:
            d = 16
        
        # Max upwards force
        if d < 0:
            d -= 2
        
        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
        
    def draw(self, screen):
        self.img_count += 1

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2
        else:
            if self.img_count < self.ANIMATION_TIME:
                self.img = self.IMGS[0]
            elif self.img_count < self.ANIMATION_TIME * 2:
                self.img = self.IMGS[1]
            elif self.img_count < self.ANIMATION_TIME * 3:
                self.img = self.IMGS[2]
            elif self.img_count < self.ANIMATION_TIME * 4:
                self.img = self.IMGS[1]
            elif self.img_count == self.ANIMATION_TIME * 4 + 1:
                self.img = self.IMGS[0]
                self.img_count = 0

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)

        screen.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 150
    VEL = 5
    PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
    PIPE_BOTTOM = PIPE_IMG

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        
        self.passed = False
        self.set_height()
    
    def set_height(self):
        self.height = random.randrange(50, 350)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
    
    def move(self):
        self.x -= self.VEL
    
    def draw(self, screen):
        screen.blit(self.PIPE_TOP, (self.x, self.top))
        screen.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        bottom_col_point = bird_mask.overlap(bottom_mask, bottom_offset)
        top_col_point = bird_mask.overlap(top_mask, top_offset)

        if bottom_col_point or top_col_point:
            return True
        return False
    
class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMG, (self.x1, self.y))   
        screen.blit(self.IMG, (self.x2, self.y))


def draw_window(screen, birds, pipes, base, score):
    screen.blit(BACKGROUND_iMG, (0,0))

    for pipe in pipes:
        pipe.draw(screen)

    text = STAT_FONT.render(f"Score: {score}", 1,(255,255,255))
    screen.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))

    base.draw(screen)
    
    for bird in birds:
        bird.draw(screen)
    pygame.display.update()

def main(genomes, config):
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(BIRD_X,200))
        g.fitness = 0
        ge.append(g)

    
    base = Base(600)
    pipes = [Pipe(600)]

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    run = True
    while run:
        clock.tick(34)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            #output = nets[x].activate((pipes[pipe_ind].x, bird.y - pipes[pipe_ind].bottom))
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom), pipes[pipe_ind].x))
            #output = nets[x].activate((bird.y - pipes[pipe_ind].bottom - 75, pipes[pipe_ind].x))

            if output[0] > 0.5:
                bird.jump()
                

        rem = []
        add_pipe = False
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(500))
                
        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() > base.y or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)


        base.move()
        
        draw_window(screen, birds, pipes, base, score)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    #generations = 50
    winner = p.run(main ,50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)

