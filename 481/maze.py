from player import Player
from random import randint
import sys

# read input file and parse data
def init_escape():
    with open('input.txt', 'r') as f:
        data =  f.readlines()

    origin = (int(data[0].strip().split(',')[0][1:]), int(data[0].strip().split(',')[1][0:-1]))
    escape = (int(data[1].strip().split(',')[0][1:]), int(data[1].strip().split(',')[1][0:-1]))

    danger_zone = []
    spider_net = []
    for sand in data[2].strip().split(' '):
        danger_zone.append((int(sand.split(',')[0][1:]), int(sand.split(',')[1][0:-1])))
    for spider in data[3].strip().split(' '):
        spider_x = int(spider.split(',')[0][1:])
        spider_y = int(spider.split(',')[1][0:-1])
        spider_net.append((spider_x, spider_y))
        danger_zone.append((spider_x, spider_y))
        danger_zone.append((spider_x-1, spider_y))
        danger_zone.append((spider_x+1, spider_y))
        danger_zone.append((spider_x, spider_y+1))
        danger_zone.append((spider_x, spider_y-1))

    fees = {}
    for fee in data[4].strip().split(' '):
        fees.update({(int(fee.split(':')[1].split(',')[0][1:]), int(fee.split(':')[1].split(',')[1][0:-1])): int(fee.split(':')[0])})

    return origin, escape, danger_zone, spider_net, fees

# calculate cost
# return infinity if it is a boundary or danger detected
def heuristic(coord, end):
    if coord[0]:
        dx = abs(coord[0][0] - end[0])
        dy = abs(coord[0][1] - end[1])
        return coord[1] * (dx + dy)
    return float('inf')

def tie_heuristic(coord, begin, end, cost):
    dx1 = coord[0] - end[0]
    dy1 = coord[1] - end[1]
    dx2 = begin[0] - end[0]
    dy2 = begin[1] - end[1]
    return cost + abs((dx1 * dy2) - (dx2 * dy1)) * 0.001

# log all the things!
def log(msg, debug):
    if debug:
        print(msg)

# save output to file
def output(msg):
    with open('output.txt', 'w') as f:
        f.write(msg)

# display the maze
def display_maze(maze, spider, danger, fees):
    # display spider net coverage
    t = []
    for i in spider:
        t.append((i[0]+1, i[1]))
        t.append((i[0]-1, i[1]))
        t.append((i[0], i[1]+1))
        t.append((i[0], i[1]-1))
    for i in t:
        spider.append(i)
    # overlay traps on map
    for quick in danger:
        maze[quick[1]][quick[0]] = 2
    for net in spider:
        maze[net[1]][net[0]] = 3
    for fee in fees.keys():
        maze[fee[1]][fee[0]] = 4
    # print the maze
    for i in maze:
        s = ''
        for j in i:
            if j == 0:
                s += '.'
            elif j == 2:
                s += 'Q'
            elif j == 3:
                s += 'S'
            elif j == 4:
                s += 'F'
            elif j == 5:
                s += 'X'
            else:
                s += '@'
        log(s, True)

def main(debug=False):
    # build the maze
    maze = []
    for i in range(0, 20):
        temp = []
        for j in range(0, 20):
            temp.append(1)
        maze.append(temp)
    # initialize the data
    begin, end, danger, spider, fees = init_escape()
    p = Player(begin, end, danger, spider, fees, debug)
    # do the things
    maze[begin[1]][begin[0]] = 0
    # https://en.wikipedia.org/wiki/Hill_climbing#Pseudocode
    move_it_move_it = [p.up, p.down, p.left, p.right]
    directions = [p.check_up, p.check_down, p.check_left, p.check_right]
    d = ['Up', 'Down', 'Left', 'Right']
    log('\nStart: {0}\nEnd: {1}\n'.format(str((begin[0], begin[1])), str((end[0], end[1]))), debug)

    # keep searching for the exit or until agent is captured
    while p.current_position() != end and not p.captured:
        try:
            cost = float('inf')
            move = -1
            vals = {}
            for index, node in enumerate(directions):
                node_result = node()
                evaluated_cost = p.cost + heuristic(node_result, end)
                if evaluated_cost != float('inf'):
                    if evaluated_cost == 0:
                        move = index
                        cost = evaluated_cost
                    elif evaluated_cost < cost:
                        cost = evaluated_cost
                        move = index
                    elif evaluated_cost == cost:
                        vals.update({move: directions[move]()})
                        vals.update({index: node_result})
                        move = index
                        rngesus = evaluated_cost
                    log('{0} - Cost: {1} - Checking: {2} - Weight: {3} - Evaluated Cost: {4}'.format(d[index], cost, node_result[0], node_result[1], evaluated_cost), debug)
                else:
                    log('{0} is either a trap or a boundary!'.format(d[index]), debug)
            if len(vals) > 0:
                if rngesus <= cost:
                    cost = float('inf')
                    log('\nCollision detected. Calculating weight with cross-product.', debug)
                    for collision in vals:
                        evaluated_cost = tie_heuristic(vals[collision][0], begin, end, heuristic(vals[collision], end))
                        if evaluated_cost < cost:
                            move = collision
                            cost = evaluated_cost
                        elif evaluated_cost == cost:
                            log('Detected another collision. Let\'s randomize now.', debug)
                            move = 4
                        log('{0} - Cost: {1} - Checking: {2} - Weight: {3} - Evaluated Cost: {4}'.format(d[collision], cost, vals[collision][0], vals[collision][1], evaluated_cost), debug)
                    if move == 4:
                        log('Shuffling: {0} - Cost: {1}'.format(vals.keys(), rngesus), debug)
                        move = list(vals.keys())[randint(0, len(vals)-1)]
            if move > -1:
                move_it_move_it[move]()
                sticky, cost = p.detect_magic('neighbor')
                if p.captured:
                    break
            else:
                log('\nUnable to move?!\n', debug)
                break
            # Are we in a bad spot?
            if p.current_position() in p.danger:
                log('Captured!\n', debug)
                p.captured = True
                break
            # Bizarro World!
            maze[p.y][p.x] = 0
        except KeyboardInterrupt:
            break

    maze[p.y][p.x] = 0
    maze[end[1]][end[0]] = 5
    display_maze(maze, spider, danger, fees)
    maze = []
    [maze.append(str(i)) for i in p.path]
    log('\nCurrent position: ({0}, {1})'.format(p.x, p.y), True)
    log('Agent captured: {0}'.format(p.captured), debug)
    log('Danger detected: {0}'.format(p.danger_zone), debug)
    log('Dangerous locations: {0}'.format(list(p.detected.keys())), debug)
    log('Total cost: ${0}'.format(p.cost), True)
    log('Total number of steps taken: {0}'.format(p.moves), True)
    log('Traveled route: {0}\n'.format(', '.join(maze)), True)
    output('Total cost: ${0}\nTotal number of steps taken: {1}\nTraveled route: {2}'.format(p.cost, p.moves, ', '.join(maze)))
    return p.moves, p.captured

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "-d" or sys.argv[1] == 'd':
            main(True)
        else:
            print('Invalid argument option.')
            sys.exit(1)
    else:
        main()
