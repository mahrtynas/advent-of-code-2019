import numpy as np

shapes = [' ', '█', 'x', '▄', 'o']

class Intcode_computer():

    def __init__(self, inputs = []):
        self.sequence = []
        self.inputs = inputs
        self.outputs = []


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
        p = 0
        rb = 0
        seq = self.sequence
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

def main():
    game = Intcode_computer()
    game.read_sequence('input.txt')
    game.run()
    
    sequence = np.array(game.outputs)
    sequence = sequence.reshape((-1, 3))
    max_x = np.max(sequence[:, 0])
    max_y = np.max(sequence[:, 1])
    board = np.full((max_y + 1, max_x + 1), ' ')
    for e in sequence:
        board[e[1], e[0]] = shapes[e[2]]
    print(f'Number of blocks: {np.sum(sequence[:,2] == 2)}')
    print("")
    for row in board:
        print(''.join(row))

    print("a\nb", end = "\r\r"),print("c")

if __name__ == "__main__":
    main()