from random import randint

class Player():
    def __init__(self, begin, end, danger, spider, fees, debug=False):
        self.x = begin[0]       # x coordinate for origin
        self.y = begin[1]       # y coordinate for origin
        self.x_it = end[0]      # x coordinate for exit
        self.y_exit = end[1]    # y coordinate for exit
        self.danger = danger    # list of quick sand and spider traps to detect
        self.spider = spider    # list of spider traps
        self.fees = fees        # dictionary of coordinates with increased value
        self.moves = 0          # keep track of total moves
        self.cost = 0           # keep track of total cost to move
        self.danger_zone = 0    # keep track of total danger detected
        self.path = []          # list of traveled path
        self.detected = {}      # list of dangerous coordinates detected
        self.captured = False   # agent captured
        self.debug = debug      # debug flag

    # move agent left
    def left(self):
        if self.x > 0:
            self.x = self.x - 1
            self.step_count()
            self.print_info('left')

    # check if it safe for agent to move
    def check_left(self):
        temp_x, temp_y = self.x, self.y
        trapped, cost = self.detect_magic('left')
        if self.x <= 0 or trapped == False:
            return False, cost
        if (temp_x-1, temp_y) in self.fees.keys():
            cost = self.fees[(self.x-1, self.y)]
        return ((temp_x-1, temp_y)), cost

    # move agent right
    def right(self):
        if self.x < 19:
            self.x = self.x + 1
            self.step_count()
            self.print_info('right')

    # check if it safe for agent to move
    def check_right(self):
        temp_x, temp_y = self.x, self.y
        trapped, cost = self.detect_magic('right')
        if self.x >= 19 or trapped == False:
            return False, cost
        if (temp_x+1, temp_y) in self.fees.keys():
            cost = self.fees[(temp_x+1, temp_y)]
        return ((temp_x+1, temp_y)), cost

    # move agent up
    def up(self):
        if self.y > 0:
            self.y = self.y - 1
            self.step_count()
            self.print_info('up')

    # check if it safe for agent to move
    def check_up(self):
        temp_x, temp_y = self.x, self.y
        trapped, cost = self.detect_magic('up')
        if self.y <= 0 or trapped == False:
            return False, cost
        if (self.x, self.y-1) in self.fees.keys():
            cost = self.fees[(self.x, self.y-1)]
        return ((temp_x, temp_y-1)), cost

    # move agent down
    def down(self):
        if self.y < 19:
            self.y = self.y + 1
            self.step_count()
            self.print_info('down')

    # check if it safe for agent to move
    def check_down(self):
        temp_x, temp_y = self.x, self.y
        trapped, cost = self.detect_magic('down')
        if self.y >= 19 or trapped == False:
            return False, cost
        if (temp_x, temp_y+1) in self.fees.keys():
            cost = self.fees[(temp_x, temp_y+1)]
        return ((temp_x, temp_y+1)), cost

    # update step count, cost, and path taken by agent
    def step_count(self):
        if self.current_position() in self.fees.keys():
            self.cost += self.fees[self.current_position()]
        else:
            self.cost += 1
        self.moves += 1
        self.path.append(self.current_position())

    # do not activate trap cards!
    # agent can only detect up to two spaces ahead
    def detect_magic(self, direction, cost=1, trapped=True):
        temp_x, temp_y = self.x, self.y
        if direction == 'left':
            scan_1 = (temp_x-1, temp_y)
            scan_2 = (temp_x-2, temp_y)
        elif direction == 'right':
            scan_1 = (temp_x+1, temp_y)
            scan_2 = (temp_x+2, temp_y)
        elif direction == 'up':
            scan_1 = (temp_x, temp_y-1)
            scan_2 = (temp_x, temp_y-2)
        elif direction == 'down':
            scan_1 = (temp_x, temp_y+1)
            scan_2 = (temp_x, temp_y+2)
        # check if user is caught in the spiders web of lies
        elif direction == 'neighbor':
            for i in [-1, 0, 1]:
                if (temp_x+i, temp_y) in self.spider:
                    trapped = False
                    cost = -1
                    self.captured = True
                if (temp_x, temp_y+i) in self.spider:
                    trapped = False
                    cost = -1
                    self.captured = True
        # check if the scan is dangerous
        if direction != 'neighbor':
            # if there is danger we better write it down
            # NOTE: Perhaps we should add the weight of scan_1 + scan_2?
            if scan_2 in self.danger or scan_2 in self.detected:
                self.detected.update({scan_2: self.current_position()})
                cost = 1000
            if scan_1 in self.danger or scan_1 in self.detected:
                self.detected.update({scan_1: self.current_position()})
                cost = 1000
                trapped = False
            else:
                cost = 1
            # return 4 //guaranteed to be random
            # increase the cost of travelling over previously visited locations
            if scan_1 in self.path:
                cost = randint(1, 6) ** self.path.count(scan_1)
                if self.debug:
                    print('{0} has been visited {1} times. New randomly calculated weight: {2}'.format(scan_1, self.path.count(scan_1), cost))
            # spider net?! surrounding area is also dangerous
            if scan_1 in self.spider:
                self.expand_spider_net(scan_1)
            if scan_2 in self.spider:
                self.expand_spider_net(scan_2)
            if cost == 1000:
                self.danger_zone += 1
        return trapped, cost

    # Peter Parker
    def expand_spider_net(self, loc):
        self.detected.update({(loc[0]+1, loc[1]): self.current_position()})
        self.detected.update({(loc[0]-1, loc[1]): self.current_position()})
        self.detected.update({(loc[0], loc[1]+1): self.current_position()})
        self.detected.update({(loc[0], loc[1]-1): self.current_position()})

    # report current position
    def current_position(self):
        return (self.x, self.y)

    # debug things
    def print_info(self, direction):
        if self.debug:
            print('Moved {0}'.format(direction))
            print('Current position: ({0}, {1}) with {2} moves costing ${3}'.format(self.x, self.y, self.moves, self.cost))
            print('\n')