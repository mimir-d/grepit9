# db csv
# gui pygame?
# proto ssl socket?

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


class Player(Sprite):
    __PLAYER_SIZE = 16

    def __init__(self, name, *args, **kwargs):
        super(Player, self).__init__(self.__create_image(name), *args, **kwargs)

    def __gen_rand_color(self):
        array = [random.random() for _ in range(3)]
        r = max(array)
        return tuple(int(255 * i/r) for i in array) + (200,)


    def __create_image(self, name):
        bg_color = (255, 255, 255, 0)
        color = self.__gen_rand_color()
        font = ImageFont.truetype('assets/arial.ttf', 13)

        # create blob
        im = Image.new('RGBA', (self.__PLAYER_SIZE, self.__PLAYER_SIZE), bg_color)
        draw = ImageDraw.Draw(im)
        draw.ellipse((1, 1, im.size[0]-1, im.size[1]-1), fill=color)

        # create name
        text_size = draw.textsize(name[:10], font=font)
        im_name = Image.new('RGBA', (im.size[0] + text_size[0], im.size[1] + text_size[1]), bg_color)
        im_name.paste(im, (0, text_size[1]))

        draw = ImageDraw.Draw(im_name)
        draw.text((self.__PLAYER_SIZE, 0), name, font=font, fill=color)

        return ImageData(*im_name.size, 'RGBA', im_name.tobytes(), pitch=-im_name.size[0]*4)


class Main(ColorLayer):
    def __init__(self):
        # super(Main, self).__init__(52//2, 152//2, 219//2, 1000)
        super(Main, self).__init__(30, 50, 70, 1000)

        for i in range(20):
            sprite = Player('1234567890')
            self.add(sprite)

            sprite.position = random.randrange(150, 600), random.randrange(150,600)
            left = act.MoveBy((-150, 0), 2)
            sprite.do(act.Repeat(left + act.Reverse(left)))



director.init(width=600, height=600, autoscale=True, resizable=True)
director.run(cocos.scene.Scene(Main()))
