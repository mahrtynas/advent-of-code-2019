import numpy as np

def read_file(path):
	with open(path, 'r') as f:
		s = f.read()
	return s

def create_layers(data, width = 25, height = 6):
	data = np.array([int(x) for x in data])
	layers = data.reshape((-1, height, width))
	return layers

def print_image(input):

	s = ''
	for i, v in enumerate(input.reshape((-1))):
		if i % 25 == 0:
			s += '\n'
		if v == 1:
			s += ' '
		else:
			s += '█'
	print(s)

def main():
	s = read_file('input.txt')
	layers = create_layers(s)
	image = np.zeros((6, 25))
	for i in range(0, 6):
		for j in range(0, 25):
			first_value = layers[:,i,j][layers[:,i,j] != 2][0]
			image[i, j] = first_value
	print_image(image)


if __name__ == "__main__":
	main()

