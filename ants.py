
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

from PIL import Image, ImageDraw, ImageFont
from pyglet.image import ImageData

import cocos
from cocos.layer import Layer, ColorLayer
from cocos import layer
from cocos.sprite import Sprite
import cocos.actions as act
from cocos.director import director


class CircleSprite(Sprite):
    def __init__(self, size, color):
        super(CircleSprite, self).__init__(self.__create_image(size, color))

    def __create_image(self, size, color):
        im = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(im)
        draw.ellipse((1, 1, im.size[0]-1, im.size[1]-1), fill=color)

        im = self._manip_image(im)
        return ImageData(*im.size, 'RGBA', im.tobytes(), pitch=-im.size[0]*4)

    def _manip_image(self, im):
        return im


class Player(CircleSprite):
    __SIZE = 24

    def __init__(self, name):
        self.name = name[:10]
        super(Player, self).__init__(self.__SIZE, self.__gen_rand_color())

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


class Feeder(CircleSprite):
    __SIZE = 80

    def __init__(self):
        super(Feeder, self).__init__(self.__SIZE, (128, 255, 128, 240))


class Food(CircleSprite):
    __SIZE = 12

    def __init__(self):
        super(Food, self).__init__(self.__SIZE, (255, 255, 0, 200))


class Main(ColorLayer):
    def __init__(self):
        super(Main, self).__init__(52, 152, 219, 70)

        for i in range(20):
            sprite = Player('1234567890')
            self.add(sprite, z=1)

            sprite.position = random.randrange(150, 800), random.randrange(150,800)
            left = act.MoveBy((-150, 0), 2)
            sprite.do(act.Repeat(left + act.Reverse(left)))

        for i in range(10):
            food = Food()
            self.add(food, z=1)

            food.position = random.randrange(10, 790), random.randrange(10, 790)

        self.__init_map()

    def __init_map(self):
        feeder = Feeder()
        feeder.position = 400, 400
        self.add(feeder, z=-1)


if __name__ == '__main__':
    director.init(width=800, height=800, autoscale=True, resizable=True)
    director.run(cocos.scene.Scene(Main()))
