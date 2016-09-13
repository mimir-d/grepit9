

from ants import PlayerAI


def dist(x0, y0, x1, y1):
    return ((x0-x1)*(x0-x1) + (y0-y1)*(y0-y1)) ** 0.5


class Player(PlayerAI):
    def __init__(self):
        super(Player, self).__init__('paulb')
        self.players_closest_foods=[]

    def updatePlayersClosestFoods(self,player_positions, food_positions):
        bla = 2

    def getFoodsSorted(self,player,food_positions_original):
        food_positions = food_positions_original[:]
        for i in range (0,len(food_positions)-1):
            for j in range (i+1,len(food_positions)):
                distanceI = dist(player[0],food_positions[i][0],player[1],food_positions[i][1])
                distanceJ = dist(player[0],food_positions[j][0],player[1],food_positions[j][1])
                if distanceI > distanceJ:
                    aux = food_positions[i]
                    food_positions[i]=food_positions[j]
                    food_positions[j]=aux
        return food_positions

    def changePlayerPosition(self,player_positions):
        for i in range(0,len(player_positions)):
            if self.position[0] == player_positions[i][0] and self.position[1] == player_positions[i][1]:
                aux = player_positions[0]
                player_positions[0]=player_positions[i]
                player_positions[i] = aux
        return player_positions

    def pointInRect(self,x,y,left,right,bottom,top):
        return x >= left and x<=right and y>=bottom and y<=top


    def update(self, player_positions, player_lives, food_positions):

        # player_positions=self.changePlayerPosition(player_positions)
        # players_closest_foods = []
        # for player in player_positions:
        #     players_closest_foods.append(self.getFoodsSorted(player,food_positions))
        #
        #
        # return players_closest_foods[0][0][0] - self.position[0], players_closest_foods[0][0][1] - self.position[1]
        #

        rects=[[0,400,0,400],[400,800,0,400],[0,400,400,800],[400,800,400,800]]
        counts=[0,0,0,0]
        for i in range(0,len(rects)):
            rect = rects[i]
            for food in food_positions:
                if self.pointInRect(food[0],food[1],rect[0],rect[1],rect[2],rect[3]):
                    counts[i] = counts[i] +1
        bestRectIndex = -1
        bestRectCount = -1
        for i in range(0,len(rects)):
            if counts[i] >= bestRectCount:
                bestRectCount = counts[i]
                bestRectIndex = i

        if not self.pointInRect(self.position[0],self.position[1],rects[bestRectIndex][0],rects[bestRectIndex][1],rects[bestRectIndex][2],rects[bestRectIndex][3]):
            return (rects[bestRectIndex][0]+rects[bestRectIndex][1])/2 - self.position[0], (rects[bestRectIndex][2]+rects[bestRectIndex][3])/2 - self.position[1]

        food_pos = None
        for food in food_positions[:]:
            min_dist=100000
            for f in player_positions:
                d = dist(food[0], food[1], f[0], f[1])
                if d < min_dist:
                    min_dist = d
                    closest_food = f
            if f[0] == self.position[0] and f[1] == self.position[1]:
                food_pos = food
            food_positions.remove(food)


        if food_pos == None:
            return 400 - self.position[0], 400 - self.position[1]
        return food_pos[0] - self.position[0], food_pos[1] - self.position[1]
