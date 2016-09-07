
# objects:
#   1. map 800x800
#   2. entity 25x25
#   3. food 12x12

# game mechanics:
#   1. big circle in middle with +0.1/s
#   2. walls kills
#   3. obstacles -0.5/s
#   4. collisions -1/s when delta > 3
#   5. food gives 1

import random
import math
import os
import importlib

from PIL import Image, ImageDraw, ImageFont
from pyglet.image import ImageData

import cocos
import cocos.actions as act
import cocos.euclid as eu
import cocos.collision_model as cm
from cocos.layer import Layer, ColorLayer
from cocos.sprite import Sprite
from cocos.director import director


class CircleEntity(Sprite):
    def __init__(self, size, color):
        super(CircleEntity, self).__init__(self.__create_image(size, color))
        self.__init_phys(size)
        self.life = 0

    def __create_image(self, size, color):
        im = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(im)
        draw.ellipse((1, 1, im.size[0]-1, im.size[1]-1), fill=color)

        im = self._manip_image(im)
        return ImageData(*im.size, 'RGBA', im.tobytes(), pitch=-im.size[0]*4)

    def _manip_image(self, im):
        return im

    def __init_phys(self, size):
        self.cshape = cm.CircleShape(eu.Vector2(0, 0), size/2)

    def update(self):
        self.cshape.center = eu.Vector2(*self.position)


class Player(CircleEntity):
    __SIZE = 25

    def __init__(self, name):
        self.name = name[:10]
        super(Player, self).__init__(self.__SIZE, self.__gen_rand_color())
        self.life = 1
        self.velocity = (0, 0)

    def __gen_rand_color(self):
        array = [random.random() for _ in range(3)]
        r = max(array)
        return tuple(int(255 * i/r) for i in array) + (200,)

    def _manip_image(self, im):
        font = ImageFont.truetype('assets/arial.ttf', 15)
        draw = ImageDraw.Draw(im)
        text_size = draw.textsize(self.name, font=font)

        # create name
        im_name = Image.new('RGBA', (im.size[0] + text_size[0], im.size[1] + text_size[1]), (255, 255, 255, 0))
        im_name.paste(im, (0, text_size[1]))

        draw = ImageDraw.Draw(im_name)
        draw.text((im.size[0], 0), self.name, font=font, fill=self.color[:3])

        return im_name

    def __str__(self):
        return 'Player:{}'.format(self.name)


class Feeder(CircleEntity):
    __SIZE = 80

    def __init__(self):
        super(Feeder, self).__init__(self.__SIZE, (128, 255, 128, 240))


class Food(CircleEntity):
    __SIZE = 12

    def __init__(self):
        super(Food, self).__init__(self.__SIZE, (255, 255, 0, 200))
        self.life = 1


class Main(ColorLayer):
    WIDTH = 800
    HEIGHT = 800

    def __init__(self):
        super(Main, self).__init__(52, 152, 219, 70)
        self.collision_manager = cm.CollisionManagerBruteForce()

        self.__init_map()
        self.__init_food()
        self.__init_players()

        self.schedule(self.__update)

    def add(self, obj, *args, **kwargs):
        super(Main, self).add(obj, *args, **kwargs)
        self.collision_manager.add(obj)

    def __init_map(self):
        self.feeder = Feeder()
        self.feeder.position = self.WIDTH//2, self.HEIGHT//2
        self.add(self.feeder, z=-1)

    def __init_players(self):
        self.__players = []

        for fn in os.listdir('ai'):
            if fn[:6] != 'player':
                continue
            mod_name = os.path.splitext(fn)[0]
            mod = importlib.import_module('ai.{}'.format(mod_name))

            ai = mod.Player()
            p = Player(ai.name)
            p.position = 10, 10

            p.do(MoveAI(ai, self.__players, self.__food))

            self.__players.append(p)
            self.add(p)

        # p1 = Player('1')
        # p2 = Player('2')
        # p1.position = 10, 10
        # p2.position = 100, 100

        # mv = act.MoveBy((500, 500), 3)
        # p1.do(act.Repeat(mv + act.Reverse(mv)))
        # p2.do(act.Repeat(act.Reverse(mv) + mv))

        # self.__players.append(p1)
        # self.__players.append(p2)

        # self.add(p1)
        # self.add(p2)
        # p2.life = 10
        # for i in range(20):
        #     p = Player('123')
        #     self.__players.append(p)

        #     self.add(p, z=1)

        #     # TODO:
        #     p.position = random.randrange(150, 800), random.randrange(150, 800)
        #     left = act.MoveBy((-150, 0), 2)
        #     sprite.do(act.Repeat(left + act.Reverse(left)))

    def __init_food(self):
        self.__food = []

        for i in range(10):
            food = Food()
            food.position = random.randrange(10, self.WIDTH-10), random.randrange(10, self.HEIGHT-10)
            self.__food.append(food)
            self.add(food, z=1)


    def __update(self, dt):
        # update physics positions
        self.feeder.update()

        for p in self.__players:
            p.update()

        for f in self.__food:
            f.update()

        for c1, c2 in self.collision_manager.iter_all_collisions():
            if type(c1) is Player and type(c2) is Player:
                if c1.life > 0 and c2.life > 0 and math.fabs(c1.life - c2.life) > 3:
                    c1.life -= dt
                    c2.life -= dt
            elif type(c1) is Food and type(c2) is Player and c1.life > 0:
                c1.life = 0
                c2.life += 1
            elif type(c1) is Player and type(c2) is Food and c2.life > 0:
                c1.life += 1
                c2.life = 0
            elif type(c1) is Feeder and type(c2) is Player:
                c2.life += 0.1 * dt
            elif type(c1) is Player and type(c2) is Feeder:
                c1.life += 0.1 * dt
        # print(self.__players[0].life, self.__players[1].life)

        # update lives
        dead_players = []
        for p in self.__players:
            if p.life <= 0 or p.position[0] < 10 or p.position[0] > self.WIDTH-10 or p.position[1] < 10 or p.position[1] > self.HEIGHT-10:
                dead_players.append(p)

        for p in dead_players:
            # removing from layer crashes with error now
            self.__players.remove(p)
            p.remove_action(p.actions[0])
            p.position = -100, -100
            print('{} died'.format(p))

        for f in self.__food:
            if f.life <= 0:
                # respawn it
                f.position = random.randrange(10, self.WIDTH-10), random.randrange(10, self.HEIGHT-10)
                f.life = 1


class MoveAI(act.Move):
    __SPEED = 5

    def __init__(self, ai, players, food, *args, **kwargs):
        super(MoveAI, self).__init__(*args, **kwargs)
        self.__ai = ai
        self.__players = players
        self.__food = food

    def step(self, dt):
        super(MoveAI, self).step(dt)

        dx, dy = self.__ai.update(
            [p.position for p in self.__players],
            [f.position for f in self.__food]
        )

        # normalize
        mag = (dx*dx + dy*dy) ** 0.5
        dx /= mag
        dy /= mag

        self.target.position = (
            self.target.position[0] + dx * self.__SPEED,
            self.target.position[1] + dy * self.__SPEED
        )
        self.__ai.position = self.target.position[:]

    def __deepcopy__(self, memo):
        # the framework does a deepcopy on the action, and i need the players and food refs to
        # work so this deepcopy override needs to be here
        return self


class PlayerAI:
    def __init__(self, name):
        self.position = (0, 0)
        self.name = name


if __name__ == '__main__':
    director.init(width=Main.WIDTH, height=Main.HEIGHT, autoscale=True, resizable=True)
    director.run(cocos.scene.Scene(Main()))
