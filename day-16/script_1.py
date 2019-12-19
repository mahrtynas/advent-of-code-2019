import numpy as np

def read_input(path):
	with open(path, 'r') as f:
		number = f.read()
	sequence = np.array([int(x) for x in number])
	return sequence

def FFT(seq, phases = 4, pattern = [0, 1, 0, -1]):
	n = len(seq)
	pattern = np.array(pattern)
	patterns = np.zeros((n, n))
	for i in range(0, n):
		p = np.repeat(pattern, i + 1)
		tiles = int(np.ceil(n / len(p))) + 1
		patterns[i] = np.tile(p, tiles)[1:(n+1)]
	phase = 0
	while phase != phases:
		phase += 1 
		seq = np.sum(np.tile(seq, (n, 1)) * patterns, axis = 1)
		seq = np.remainder(np.abs(seq), 10)
	return seq

def main():
	seq = read_input('input.txt')
	new_seq = FFT(seq, 100)
	print(f'First eight digits {"".join([str(int(x)) for x in new_seq[0:8]])}')

if __name__ == "__main__":
	main()
