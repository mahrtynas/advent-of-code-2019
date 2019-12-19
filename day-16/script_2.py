import numpy as np

def read_input(path):
	with open(path, 'r') as f:
		number = f.read()
	sequence = np.array([int(x) for x in number])
	return sequence

def main():
	seq = read_input('input.txt')
	seq = np.tile(seq, 10000)
	offset = int("".join([str(int(x)) for x in seq[0:7]]))	
	n = len(seq)
	assert offset > n / 2
	subseq = seq[offset:]
	n = len(subseq)
	for p in range(0, 100):
		print(f'Phase {p + 1}')
		subseq = np.flip(np.cumsum(np.flip(subseq)))
		subseq = np.mod(subseq, 10)
	print(f'First eight digits {"".join([str(int(x)) for x in subseq[0:8]])}')

if __name__ == "__main__":
	main()
