
# objects:
#   1. map 600x600
#   2. entity 15x15

# game mechanics:
#   1. big circle in middle with +0.1/s
#   2. walls kills
#   3. obstacles -0.5/s
#   4. collisions -1/s when delta > 5
#   5. food gives 1

import random
import math

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
        return self.name


class Feeder(CircleEntity):
    __SIZE = 80

    def __init__(self):
        super(Feeder, self).__init__(self.__SIZE, (128, 255, 128, 240))


class Food(CircleEntity):
    __SIZE = 12

    def __init__(self):
        super(Food, self).__init__(self.__SIZE, (255, 255, 0, 200))
        # TODO:
        self.alive = True


class Main(ColorLayer):
    WIDTH = 800
    HEIGHT = 800

    def __init__(self):
        super(Main, self).__init__(52, 152, 219, 70)
        self.collision_manager = cm.CollisionManagerBruteForce()

        self.__init_map()
        self.__init_players()
        self.__init_food()

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

        p1 = Player('1')
        p2 = Player('2')
        p1.position = 10, 10
        p2.position = 100, 100

        mv = act.MoveBy((100, 100), 5)
        p1.do(act.Repeat(mv + act.Reverse(mv)))
        p2.do(act.Repeat(act.Reverse(mv) + mv))

        self.__players.append(p1)
        self.__players.append(p2)

        self.add(p1)
        self.add(p2)
        p2.life = 10
        # for i in range(20):
        #     p = Player('123')
        #     self.__players.append(p)

        #     self.add(p, z=1)

        #     # TODO:
        #     p.position = random.randrange(150, 800), random.randrange(150, 800)
        #     left = act.MoveBy((-150, 0), 2)
        #     sprite.do(act.Repeat(left + act.Reverse(left)))

    def __init_food(self):
        # for i in range(10):
        #     food = Food()
        #     self.add(food, z=1)

        #     food.position = random.randrange(10, 790), random.randrange(10, 790)
        pass

    def __update(self, dt):
        self.feeder.update()

        dead_players = []
        for p in self.__players:
            p.update()
            if p.life <= 0:
                dead_players.append(p)

        for p in dead_players:
            # removing from layer crashes with error now
            self.__players.remove(p)
            p.remove_action(p.actions[0])
            p.position = -100, -100

        for c1, c2 in self.collision_manager.iter_all_collisions():
            if type(c1) is Player and type(c2) is Player:
                if c1.life > 0 and c2.life > 0 and math.fabs(c1.life - c2.life) > 5:
                    c1.life -= dt
                    c2.life -= dt


if __name__ == '__main__':
    director.init(width=Main.WIDTH, height=Main.HEIGHT, autoscale=True, resizable=True)
    director.run(cocos.scene.Scene(Main()))
