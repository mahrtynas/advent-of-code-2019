from multiprocessing import Process, Queue
from threading import Lock
import time

class Intcode_computer():

    def __init__(self, inputs = []):
        self.sequence = []
        self.input_queue = Queue()
        self.inputs = inputs
        self.outputs = []
        self.p = 0
        self.rb = 0
        self.state = "initiated"

    def add_to_network(self, network):
        self.network = network

    def send_packet(self, packet):
        address = packet[0]
        values = packet[1:3]
        if packet[0] < 50:
            self.network[address].input_queue.put(values)
        else:
            self.network[255].input_queue.put(values)

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
            seq += [0] * (pops[2] - len(seq) + 1)
            seq[pops[2]] = ops[0] * ops[1]
        return seq

    def seq_input(self, pops, input):
        seq = self.sequence
        if len(seq) > pops[0]:
            seq[pops[0]] = input
        else:
            seq += [0] * (pops[0] - len(seq) + 1)
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
        while len(seq) <= pops[2]:
            seq.append(0)
        seq[pops[2]] = 1 * (ops[0] < ops[1])
        return seq

    def equal(self, ops, pops):
        seq = self.sequence
        if len(seq) > pops[2]:
            seq[pops[2]] = 1 * (ops[0] == ops[1])
        else:
            seq += [0] * (pops[2] - len(seq) + 1)
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
            if operation == 1:
                seq = self.add(ops, pops)
                p += 4
            if operation == 2:
                seq = self.multiply(ops, pops)
                p += 4
            if operation == 3:
                if len(self.inputs) > 0:
                    inp = self.inputs.pop(0)
                    seq = self.seq_input(pops, inp)
                elif not self.input_queue.empty():
                    self.inputs = self.input_queue.get_nowait()
                    inp = self.inputs.pop(0)
                    seq = self.seq_input(pops, inp)
                else:
                    seq = self.seq_input(pops, -1)
                p += 2   
            if operation == 4:
                self.outputs.append(self.seq_output(seq, pops))
                if len(self.outputs) > 2:
                    packet = [self.outputs.pop(0) for x in range(0, 3)]
                    self.send_packet(packet)
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

class NAT():
    def __init__(self, network):
        self.input_queue = Queue()
        self.inputs = []
        self.network = network
        self.invoked_y = []

    def process_queue(self):
        while not self.input_queue.empty():
            values = self.input_queue.get_nowait()
            self.inputs = values

    def check_computers(self):
        idle_computers = 0
        for computer in self.network:
            idle_computers += int(computer.input_queue.empty())
        if idle_computers == 50:
            return "idle"
        else:
            return "running"

    def send_packet(self):
        address = 0
        values = self.inputs
        self.network[address].input_queue.put(values)

    def monitor(self):
        while True:
            time.sleep(3)
            if self.check_computers() == "idle":
                self.process_queue()
                print(f'Invoking network with values {self.inputs}')
                self.invoked_y.append(self.inputs[1])
                duplicated = [i for i in self.invoked_y if self.invoked_y.count(i) > 1]
                if len(duplicated) > 0:
                    print(f'Repeated Y value = {duplicated}')
                self.send_packet()

def main():
    network = []
    for i in range(0, 50):
        network.append(Intcode_computer([i]))
        network[i].read_sequence('input.txt')
        network[i].add_to_network(network)
    for i in range(0, 206):
        network.append(None)
    network[255] = NAT(network[0:50])
    for i in range(0, 50):
        Process(target = network[i].run).start()
    Process(target = network[255].monitor).start()


if __name__ == "__main__":
    main()