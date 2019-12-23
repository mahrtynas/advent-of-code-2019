import curses
import time

class Intcode_computer():

    def __init__(self, inputs = []):
        self.sequence = []
        self.inputs = inputs
        self.outputs = []
        self.p = 0
        self.rb = 0
        self.state = "initiated"

    def read_sequence(self, path):
        with open(path, 'r') as f:
            seq = f.read()
        self.sequence = [int(x) for x in seq.split(",")]

    def get_operation(self, x):
        return int(str(x)[-2:])

    def get_modes(self, x):
        modes = [int(i) for i in str(x)[:-2][::-1]]
        modes += [0] * (3 - len(modes))
        return(modes)

    def get_operands(self, modes, op, rb = 0):
        seq = self.sequence
        ops = []
        for i, m in enumerate(modes):
            if m == 0:
                try: 
                    ops += [seq[seq[op + i + 1]]]
                except:
                    ops += [0]
            elif m == 1:
                try: 
                    ops += [seq[op + i + 1]]
                except:
                    ops += [0]
            elif m == 2:
                try:
                    ops += [seq[seq[op + i + 1] + rb]]
                except:
                    ops += [0]
        return ops

    def get_positional_operands(self, modes, op, rb = 0):
        seq = self.sequence
        ops = []
        for i, m in enumerate(modes):
            if m == 0:
                try: 
                    ops += [seq[op + i + 1]]
                except:
                    ops += [0]
            elif m == 1:
                try: 
                    ops += [op + i + 1]
                except:
                    ops += [0]
            elif m == 2:
                try:
                    ops += [seq[op + i + 1] + rb]
                except:
                    ops += [0]
        return ops

    def add(self, ops, pops):
        seq = self.sequence
        if len(seq) > pops[2]:
            seq[pops[2]] = ops[0] + ops[1]
        else:
            seq += [0] * (pops[2] - len(seq) + 1)
            seq[pops[2]] = ops[0] + ops[1]
        return seq
            
    def multiply(self, ops, pops):
        seq = self.sequence
        if len(seq) > pops[2]:
            seq[pops[2]] = ops[0] * ops[1]
        else:
            seq += [None] * (pops[2] - len(seq) + 1)
            seq[pops[2]] = ops[0] * ops[1]
        return seq

    def seq_input(self, pops, input):
        seq = self.sequence
        if len(seq) > pops[0]:
            seq[pops[0]] = input
        else:
            seq += [None] * (pops[0] - len(seq) + 1)
            seq[pops[0]] = input
        return seq

    def seq_output(self, seq, pops):
        try:
            return seq[pops[0]]
        except:
            return None
            
    def jump_if_true(self, ops, pops, op):
        if ops[0] != 0:
            op = ops[1]
        else:
            op += 3
        return op

    def jump_if_false(self, ops, pops, op):
        if ops[0] == 0:
            op = ops[1]
        else:
            op += 3
        return op

    def less_than(self, seq, ops, pops):
        seq[pops[2]] = 1 * (ops[0] < ops[1])
        return seq

    def equal(self, ops, pops):
        seq = self.sequence
        if len(seq) > pops[2]:
            seq[pops[2]] = 1 * (ops[0] == ops[1])
        else:
            seq += [None] * (pops[2] - len(seq) + 1)
            seq[pops[2]] = 1 * (ops[0] == ops[1])
        return seq

    def change_rb(self, ops, rb):
        return rb + ops[0]

    def run(self):
        p = self.p
        rb = self.rb
        seq = self.sequence
        self.state = "running"
        while seq[p] != 99:
            value = seq[p]
            operation = self.get_operation(value)
            modes = self.get_modes(value)
            ops = self.get_operands(modes, p, rb)
            pops = self.get_positional_operands(modes, p, rb)
            #print(f'value = {value}, rb = {rb}, modes = {modes}, ops = {ops}, pops = {pops}')
            if operation == 1:
                seq = self.add(ops, pops)
                p += 4
            if operation == 2:
                seq = self.multiply(ops, pops)
                p += 4
            if operation == 3:
                if len(self.inputs) > 0:
                    seq = self.seq_input(pops, self.inputs.pop(0))
                else:
                    self.state = "paused"
                    self.p = p
                    self.rb = rb
                    return
                p += 2   
            if operation == 4:
                self.outputs.append(self.seq_output(seq, pops))
                p += 2
            if operation == 5:
                p = self.jump_if_true(ops, pops, p)
            if operation == 6:
                p = self.jump_if_false(ops, pops, p)
            if operation == 7:
                seq = self.less_than(seq, ops, pops)
                p += 4
            if operation == 8:
                seq = self.equal(ops, pops)
                p += 4
            if operation == 9:
                rb = self.change_rb(ops, rb)
                p += 2
        self.state = "completed"

def next_move_after_block(prev_move):
    if prev_move == 1:
        return 3
    elif prev_move == 2:
        return 4
    elif prev_move == 3:
        return 2
    else:
        return 1

def next_move_non_block(prev_move):
    if prev_move == 1:
        return 4
    elif prev_move == 2:
        return 3
    elif prev_move == 3:
        return 1
    else:
        return 2

def get_new_coord(current_coord, move):
    new_coord = current_coord.copy()
    if move == 1:
        new_coord[1] += 1
    elif move == 2:
        new_coord[1] -= 1
    elif move == 3:
        new_coord[0] -= 1
    else:
        new_coord[0] += 1
    return new_coord

class O2Tank():
    def __init__(self, path, oxygen_coordinates):
        self.path = path
        self.oxygen = oxygen_coordinates
        self.time = 1
        self.spread_path = [[oxygen_coordinates]]

    def spread_oxygen(self):
        oxygen_path = []
        spread = [self.oxygen]
        while len(spread) > 0:
            new_spread = []
            for i in spread:
                oxygen_path.append(i)
                sp = [[i[0], i[1] + 1], [i[0], i[1] - 1], [i[0] + 1, i[1]], [i[0] - 1, i[1]]]
                sp = [x for x in sp if (x not in oxygen_path) and (x in self.path)]
                if len(sp) > 0:
                    oxygen_path.extend(sp)
                    new_spread.extend(sp)
            spread = new_spread.copy()
            self.spread_path.append(spread)
            self.time += 1



def main():
    robot = Intcode_computer()
    robot.read_sequence('input.txt')
    screen = curses.initscr()
    curses.noecho()
    curses.curs_set(0)
    screen.clear()
    screen.refresh()
    speed = 1
    path = [[0, 0]]
    oxygen_coordinates = None
    # robot first move north and if robot hits the wall turn 90 degrees and then back
    next_move = 1
    position = get_new_coord(path[-1], next_move)
    screen.addstr(25, 30, 'X')
    moves = [next_move]
    # exploring map
    robot.inputs.append(next_move)
    while robot.state != "completed":
        #screen.addstr(40, 0, f'Moves: {moves}')
        robot.run()
        #print(f'Path so far: {path}')
        #print(f'Tried position:{position}')
        #print(f'Robot outputs: {robot.outputs}')
        while len(robot.outputs) > 0:
            response = robot.outputs.pop(0)
            if response == 0:
                next_move = next_move_after_block(moves[-1])
                screen.addstr(
                    -position[1] + 25, 
                    position[0] + 30, 
                    '█')
            elif response == 1:
                path.append(position)
                next_move = next_move_non_block(moves[-1])
            else:
                screen.addstr(
                   -position[1] + 25, 
                   position[0] + 30, 
                    'O', curses.A_BLINK)
                oxygen_coordinates = get_new_coord(path[-1], next_move)
                path.append(position)
                screen.addstr(25, 70, f'Oxygen: {oxygen_coordinates}')
                next_move = next_move_non_block(moves[-1])
        position = get_new_coord(path[-1], next_move)
        if (len(path) > 2) and path[-2:] == path[0:2]:
            robot.state = "completed"
        moves.append(next_move)
        robot.inputs.append(next_move)
        screen.refresh()
        curses.napms(speed)
    curses.napms(1000)
    oxy = O2Tank(path, oxygen_coordinates)
    oxy.spread_oxygen()

    for t, points in enumerate(oxy.spread_path):
        screen.addstr(20, 70, f'Time: {t + 1}')
        for p in points:
            screen.addstr(-p[1] + 25, p[0] + 30, "o")
        screen.refresh()
        curses.napms(1000)
    curses.napms(5000)
    screen.clear()
    curses.endwin()
    print(oxy.spread_path[1:10])

if __name__ == "__main__":
    main()