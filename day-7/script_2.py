from itertools import permutations
import asyncio

def read_sequence(path):
    with open(path, 'r') as f:
        seq = f.read()
    return [int(x) for x in seq.split(",")]

def get_operation(x):
    return int(str(x)[-2:])

def get_modes(x):
    modes = [int(i) for i in str(x)[:-2][::-1]]
    modes += [0] * (3 - len(modes))
    modes[2] = 1
    if (x in [3, 4]):
        modes[0] = 1
    return(modes)

def get_operands(seq, modes, op):
    ops = []
    for i, m in enumerate(modes):
        try:
            ops += [seq[op + i + 1] * m + seq[seq[op + i + 1]] * (1 - m)]
        except:
            ops += [-1]
    return ops

def add(seq, ops):
    seq[ops[2]] = ops[0] + ops[1]
    return seq
        
def multiply(seq, ops):
    seq[ops[2]] = ops[0] * ops[1]
    return seq

def seq_input(seq, ops, input):
    seq[ops[0]] = input
    return seq

def seq_output(seq, ops):
    return seq[ops[0]]
        
def jump_if_true(seq, ops, op):
    if ops[0] != 0:
        op = ops[1]
    else:
        op += 3
    return op

def jump_if_false(seq, ops, op):
    if ops[0] == 0:
        op = ops[1]
    else:
        op += 3
    return op

def less_than(seq, ops):
    seq[ops[2]] = 1 * (ops[0] < ops[1])
    return seq

def equal(seq, ops):
    seq[ops[2]] = 1 * (ops[0] == ops[1])
    return seq

class amplifier():
    
    def __init__(self, sequence, phase, input_value = [], input_amplifier = None):
        self.sequence = sequence
        self.phase = phase
        self.inputs = [phase] + list(input_value)
        self.outputs = []
        self.input_amplifier = input_amplifier
    
    def assign_input_amplifier(self, input_amplifier):
        self.input_amplifier = input_amplifier
    
    async def run(self):
        p = 0
        seq = self.sequence
        while seq[p] != 99:
            value = seq[p]
            operation = get_operation(value)
            modes = get_modes(value)
            ops = get_operands(seq, modes, p)
            if operation == 1:
                seq = add(seq, ops)
                p += 4
            if operation == 2:
                seq = multiply(seq, ops)
                p += 4
            if operation == 3:
                if len(self.inputs) > 0:
                    seq = seq_input(seq, ops, self.inputs.pop(0))
                else:
                    while len(self.input_amplifier.outputs) == 0:
                        await asyncio.sleep(0.001)
                    seq = seq_input(seq, ops, self.input_amplifier.outputs.pop(0))
                p += 2   
            if operation == 4:
                self.outputs.append(seq_output(seq, ops))
                p += 2
            if operation == 5:
                p = jump_if_true(seq, ops, p)
            if operation == 6:
                p = jump_if_false(seq, ops, p)
            if operation == 7:
                s = less_than(seq, ops)
                p += 4
            if operation == 8:
                s = equal(seq, ops)
                p += 4

async def main():
    sequence = read_sequence("input.txt")
    phase_settings = [5, 6, 7, 8, 9]
    max_out = 0
    max_phase = []
    for p in list(permutations(phase_settings, 5)):

        # initialize all 5 amplifiers and connect them
        amplifiers = [amplifier(sequence, p[0], [0])]
        for i in range(1, 5):
            amplifiers.append(amplifier(sequence, p[i]))
            amplifiers[i].assign_input_amplifier(amplifiers[i - 1])
        amplifiers[0].assign_input_amplifier(amplifiers[4])
    
        await asyncio.gather(
            amplifiers[0].run(), 
            amplifiers[1].run(), 
            amplifiers[2].run(), 
            amplifiers[3].run(), 
            amplifiers[4].run(), 
        )

        out = amplifiers[4].outputs[0]
        if out > max_out:
            max_out = out
            max_phase = p
    print(f'Highest signal that can be sent to thrusters: {max_out}')
    print(f'Achieved with phase settings: {max_phase}')

if __name__ == "__main__":
    asyncio.run(main())
