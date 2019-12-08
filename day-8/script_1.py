import numpy as np

def read_file(path):
	with open(path, 'r') as f:
		s = f.read()
	return s

def create_layers(data, width = 25, height = 6):
	data = np.array([int(x) for x in data])
	layers = data.reshape((-1, height, width))
	return layers

def main():
	s = read_file('input.txt')
	layers = create_layers(s)
	zeros = [np.sum(x == 0) for x in layers]
	i = np.argmin(zeros)
	ones = np.sum(layers[i] == 1)
	twos = np.sum(layers[i] == 2)
	print(f'{ones}x{twos}={ones*twos}')

if __name__ == "__main__":
	main()

