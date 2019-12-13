import numpy as np

def read_positions(path):
	with open(path, 'r') as f:
		positions = f.readlines()
	return positions

def parse_value(value):
	"""
	make ' x=-1' into -1
	"""
	return int(value.split('=')[1])

def process_positions(positions):
	new_positions = []
	for p in positions:
		p = p.strip('<|>\n').split(',')
		p = [parse_value(x) for x in p]
		new_positions.append(p)
	return np.array(new_positions)

def update_velocities(positions, velocities):
	for i in range(0, positions.shape[1]):
		new_vel = (np.array([sum(-1 * (x > positions[:,i])) for x in positions[:,i]]) +
		np.array([sum(1 * (x < positions[:,i])) for x in positions[:,i]]))
		velocities[:,i] += new_vel
	return(velocities)

def detect_pattern_length(seq):
    d = 0
    max_len = int(np.floor(len(seq) / 2))
    for x in range(2, max_len):
        if np.min(seq[0:x] == seq[x:2*x]) == 1 :
            return x
    return d

def main():
	positions = read_positions('input.txt')
	positions = process_positions(positions)
	velocities = np.zeros((4, 3), dtype = "int")
	cycles = np.zeros((4, 3), dtype = "int")
	timesteps = 700000
	positions_evol = np.zeros((4, 3, timesteps), dtype = "int")
	t = 0
	for t in range(0, timesteps):
		positions_evol[:,:,t] = positions
		velocities = update_velocities(positions, velocities)
		positions += velocities
		if (t % 10000) == 0:
			print(f'Current t = {t}')
	for i in range(0, 4):
		for j in range(0, 3):
			cycles[i, j] = detect_pattern_length(positions_evol[i, j, :])
	print(cycles)
	result = np.lcm.reduce(cycles.reshape(-1), dtype = 'int')
	print(f'LCM = {result}')

if __name__ == "__main__":
	main()
