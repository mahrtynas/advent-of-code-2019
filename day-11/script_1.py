import asyncio

class Intcode_computer():

    def __init__(self, sequence, robot, inputs = []):
        self.sequence = sequence
        self.inputs = inputs
        self.outputs = []
        self.state = 'warming up'
        self.robot = robot

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

    async def run(self):
        self.state = "running"
        p = 0
        rb = 0
        seq = self.sequence
        while seq[p] != 99:
            value = seq[p]
            operation = self.get_operation(value)
            modes = self.get_modes(value)
            ops = self.get_operands(modes, p, rb)
            pops = self.get_positional_operands(modes, p, rb)
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
                    #print(f'Computer sees these imputs from robot: {self.robot.computer_inputs}')
                    while len(self.robot.computer_inputs) == 0:
                        #print(f"Waiting for robot to move")
                        await asyncio.sleep(0.001)
                    seq = self.seq_input(pops, self.robot.computer_inputs.pop(0))
                p += 2   
            if operation == 4:
                self.robot.inputs.append(self.seq_output(seq, pops))
                #self.robot.inputs.append(self.outputs[-1])
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

class Robot():
    def __init__(self):
        self.coordinates = [0, 0]
        self.path = [[0, 0]]
        self.direction = 90
        self.colors = {str([0, 0]) : '.'}
        self.inputs = []
        self.computer_inputs = [0]
        self.sequence = []
        self.moved = 0
        self.colored = 0

    def read_sequence(self, path):
        with open(path, 'r') as f:
            seq = f.read()
        self.sequence = [int(x) for x in seq.split(",")]

    async def paint_one(self, input):
        if input == 0:
            self.colors.update({str(self.coordinates): '.'})
        elif input == 1:
            self.colors.update({str(self.coordinates): '#'})
        self.colored += 1
        # print(f"Painted one {input}")

    async def move_one(self, input):
        dir = self.direction
        coord = self.coordinates
        if input == 0:
            dir = (dir + 90) % 360
        else:
            dir = (dir - 90) % 360
        self.direction = dir
        if dir == 0:
            coord = [coord[0] + 1, coord[1]]
        elif dir == 90:
            coord = [coord[0], coord[1] + 1]
        elif dir == 180:
            coord = [coord[0] - 1, coord[1] ]
        elif dir == 270:
            coord = [coord[0], coord[1] - 1]
        self.path.append(coord)
        self.coordinates = coord
        self.moved += 1
        if str(coord) in self.colors.keys():
            col = self.colors[str(coord)]
            if col == '.':
                self.computer_inputs.append(0)
            else:
                self.computer_inputs.append(1)
        else:
            self.computer_inputs.append(0)
        #print(f"Moved by 1 to {coord}")
        #print(f"Computer inputs are: {self.computer_inputs}")

    async def process(self):
        while not(self.computer.state == "completed" and len(self.inputs) == 0):
            #print(f"Robot thinks computer's state is {self.computer.state} and currently has these inputs {self.inputs}")
            while len(self.inputs) == 0:
                #print("Waiting for computer's output")
                await asyncio.sleep(0.001)
            inp = self.inputs.pop(0)
            if self.moved == self.colored:
                await self.paint_one(inp)
            elif self.moved < self.colored:
                await self.move_one(inp)


    def setup_computer(self):
        self.computer = Intcode_computer(self.sequence, self, [])

async def main():
    hull_robot = Robot()
    hull_robot.read_sequence('input.txt')
    hull_robot.setup_computer()
    await asyncio.gather(hull_robot.process(), hull_robot.computer.run())
    # print(f"Hull robot's states: {hull_robot.colors}")
    print(f"Hull robot colored these many pixels: {len(hull_robot.colors.keys())}")

if __name__ == "__main__":
    asyncio.run(main())






