
# objects:
#   1. map 800x800
#   2. entity 25x25
#   3. food 12x12

# game mechanics:
#   1. big circle in middle with +0.1/s
#   2. walls kills
#   3. collisions -1/s when delta > 3
#   4. food gives 1

import random
import math
import os
import importlib
from collections import defaultdict

from PIL import Image, ImageDraw, ImageFont
from pyglet.image import ImageData

import cocos
import cocos.actions as act
import cocos.euclid as eu
import cocos.collision_model as cm
from cocos.layer import Layer, ColorLayer
from cocos.sprite import Sprite
from cocos.text import Label
from cocos.director import director


class CircleEntity(Sprite):
    '''
    Main entity type in the simulation
    '''
    def __init__(self, size, color):
        super(CircleEntity, self).__init__(self.__create_image(size, color))
        self.__init_phys(size)
        self.life = 0

    def __create_image(self, size, color):
        im = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(im)
        draw.ellipse((1, 1, im.size[0]-1, im.size[1]-1), fill=color)

        return ImageData(*im.size, 'RGBA', im.tobytes(), pitch=-im.size[0]*4)

    def __init_phys(self, size):
        self.cshape = cm.CircleShape(eu.Vector2(0, 0), size/2)

    def update(self, dt):
        self.cshape.center = eu.Vector2(*self.position)


class Player(CircleEntity):
    '''
    Player type entity
    Eats food and fights with other players.
    '''
    __SIZE = 25

    def __init__(self, name):
        color = self.__gen_rand_color()
        super(Player, self).__init__(self.__SIZE, color)

        self.name = name[:15]

        self.__label = Label()
        self.__label.element.color = color[:3] + (255,)
        self.__label.position = (self.__SIZE/2, self.__SIZE/2)
        self.add(self.__label)

    def __gen_rand_color(self):
        array = [random.random() for _ in range(3)]
        r = max(array)
        return tuple(int(255 * i/r) for i in array) + (200,)

    def update(self, dt):
        super(Player, self).update(dt)
        self.__label.element.text = '{} -> {:.2f}'.format(self.name, self.life)

    def __str__(self):
        return 'Player:{}'.format(self.name)


class Feeder(CircleEntity):
    '''
    Feeder type entity
    Provides constant food to colliding players.
    '''
    __SIZE = 80
    __COLOR = (128, 255, 128, 240)

    def __init__(self):
        super(Feeder, self).__init__(self.__SIZE, self.__COLOR)


class Food(CircleEntity):
    '''
    Food type entity
    Provides life to players that collide with it.
    '''
    __SIZE = 12
    __COLOR = (255, 255, 0, 200)

    def __init__(self):
        super(Food, self).__init__(self.__SIZE, self.__COLOR)


class Event:
    '''
    Event object that can call multiple observer functions with arbitrary args
    '''
    def __init__(self):
        self.__observers = []

    def __iadd__(self, cb):
        self.__observers.append(cb)
        return self

    def __isub__(self, cb):
        self.__observers.remove(cb)
        return self

    def __call__(self, *args, **kwargs):
        for o in self.__observers:
            o(*args, **kwargs)


class Mechanics:
    '''
    Game mechanics object
    Deals with physics and life management
    '''
    __PLAYER_LIFE = 1
    __FOOD_LIFE = 1
    __PVP_DELTA = 1
    __PVP_DAMAGE = 2
    __FEEDER_RATE = 0.1
    __HUNGER_RATE = 0.3

    def __init__(self):
        self.__inits = {
            Feeder: self.__init_feeder,
            Player: self.__init_player,
            Food: self.__init_food
        }
        self.__collisions = {
            (Player, Player): self.__collision_pvp,
            (Player, Food):   self.__collision_pvf,
            (Food, Player):   lambda dt, f, p: self.__collision_pvf(dt, p, f),
            (Player, Feeder): self.__collision_pvfeed,
            (Feeder, Player): lambda dt, f, p: self.__collision_pvfeed(dt, p, f)
        }
        self.__collision_manager = cm.CollisionManagerBruteForce()
        self.__entities = defaultdict(lambda: [])

        self.player_death_event = Event()

    def __init_feeder(self, feeder):
        feeder.position = Main.WIDTH//2, Main.HEIGHT//2

    def __init_player(self, player):
        player.life = self.__PLAYER_LIFE
        player.position = self.__rand_position()

    def __init_food(self, food):
        food.life = self.__FOOD_LIFE
        food.position = self.__rand_position()

    def __init_null(self, entity):
        # might get called for certain objects that dont have specific mechanics
        pass

    def __collision_pvp(self, dt, p1, p2):
        if p1.life > 0 and p2.life > 0 and math.fabs(p1.life - p2.life) > self.__PVP_DELTA:
            p1.life -= self.__PVP_DAMAGE * dt
            p2.life -= self.__PVP_DAMAGE * dt

    def __collision_pvf(self, dt, player, food):
        if food.life > 0:
            player.life += food.life
            food.life = 0

    def __collision_pvfeed(self, dt, player, feeder):
        player.life += self.__FEEDER_RATE * dt

    def __collision_null(self, dt, e1, e2):
        # might get called certain collisions that should be ignored
        pass

    def __rand_position(self):
        return random.randrange(10, Main.WIDTH-10), random.randrange(10, Main.HEIGHT-10)

    def add_entity(self, entity):
        # init mechanics for given entity. state is kept inside the object itself
        init_cb = self.__inits.get(type(entity), self.__init_null)
        init_cb(entity)

        # append to known entities
        self.__entities[type(entity)].append(entity)
        self.__collision_manager.add(entity)

    def update(self, dt):
        # update all entities physics
        for k, entities in self.__entities.items():
            for e in entities:
                e.update(dt)

        # update hunger damage
        for p in self.__entities[Player]:
            p.life -= self.__HUNGER_RATE * dt

        for e1, e2 in self.__collision_manager.iter_all_collisions():
            coll_key = (type(e1), type(e2))
            coll_cb = self.__collisions.get(coll_key, self.__collision_null)
            if coll_cb is self.__collision_null:
                print(e1,e2)
            coll_cb(dt, e1, e2)

        # update lives
        dead_players = []
        for p in self.__entities[Player]:
            if p.life <= 0:
                dead_players.append(p)

            if p.position[0] < 10 or p.position[0] > Main.WIDTH-10 or p.position[1] < 10 or p.position[1] > Main.HEIGHT-10:
                # players out of bounds are also dead
                dead_players.append(p)

        for p in dead_players:
            # removing from layer crashes with error at the moment, so just remove from
            # entities list and set them to an off-screen position
            self.__entities[Player].remove(p)
            p.position = -100, -100

            self.player_death_event(p)

        for f in self.__entities[Food]:
            if f.life <= 0:
                # respawn it
                self.__inits[Food](f)

    @property
    def players(self):
        return self.__entities[Player]

    @property
    def food(self):
        return self.__entities[Food]


class Main(ColorLayer):
    WIDTH = 800
    HEIGHT = 800
    __FOOD_COUNT = 8

    def __init__(self):
        super(Main, self).__init__(52, 152, 219, 70)

        self.__mechanics = Mechanics()
        self.__mechanics.player_death_event += self.__on_player_death

        self.__init_map()
        self.__init_food()
        self.__init_players()

        self.schedule(self.__mechanics.update)

    def __on_player_death(self, player):
        # remove the MoveAI action that was added on creation
        player.remove_action(player.actions[0])
        print('{} died'.format(player))

    def add(self, obj, *args, **kwargs):
        ''' Override add() that adds physical objects as well '''
        super(Main, self).add(obj, *args, **kwargs)
        self.__mechanics.add_entity(obj)

    def __init_map(self):
        '''
        Init the map objects. So far just a single feeder.
        '''
        self.add(Feeder(), z=-1)

    def __init_players(self):
        '''
        Init players from modules in the ai directory.
        Modules need to start with 'player' prefix and contain the class
        Player inheriting PlayerAI which implements the update method.
        '''
        for fn in os.listdir('ai'):
            if fn[:6] != 'player':
                continue

            mod_name = os.path.splitext(fn)[0]
            mod = importlib.import_module('ai.{}'.format(mod_name))
            ai = mod.Player()

            p = Player(ai.name)
            p.do(MoveAI(ai, self.__mechanics))

            self.add(p)

    def __init_food(self):
        for i in range(self.__FOOD_COUNT):
            self.add(Food(), z=1)


class MoveAI(act.Move):
    __SPEED = 1.5

    def __init__(self, ai, mechanics, *args, **kwargs):
        super(MoveAI, self).__init__(*args, **kwargs)
        self.__ai = ai
        self.__mechanics = mechanics

    def step(self, dt):
        try:
            dx, dy = self.__ai.update(
                [p.position for p in self.__mechanics.players],
                [p.life for p in self.__mechanics.players],
                [f.position for f in self.__mechanics.food]
            )
        except:
            # any exception in user script results in a null movement vector
            print('{} threw exception'.format(self.target))
            dx, dy = 0, 0

        # normalize movement vector
        mag = (dx*dx + dy*dy) ** 0.5
        if math.fabs(mag) > 1e-6:
            dx /= mag
            dy /= mag

        self.target.position = (
            self.target.position[0] + dx * self.__SPEED,
            self.target.position[1] + dy * self.__SPEED
        )

        # inform the user scripts of their variables
        # NOTE: make copies, user scripts aren't allowed refs
        self.__ai.life = self.target.life
        self.__ai.position = self.target.position[:]

    def __deepcopy__(self, memo):
        # the cocos framework does a deepcopy on the action, and we need the players and food
        # refs to work in __init__ so this deepcopy override needs to be here
        return self


class PlayerAI:
    def __init__(self, name):
        self.name = name

        self.life = 0
        self.position = (0, 0)


if __name__ == '__main__':
    director.init(width=Main.WIDTH, height=Main.HEIGHT, autoscale=True, resizable=True)
    director.run(cocos.scene.Scene(Main()))
