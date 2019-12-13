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

def update_positions(positions, velocities):
	return positions + velocities

def count_energy(positions, velocities):
	total_energy = 0
	for i in range(0, positions.shape[0]):
		total_energy += np.sum(np.abs(positions[i,:])) * np.sum(np.abs(velocities[i,:]))
	return(total_energy)

def main():
	positions = read_positions('input.txt')
	positions = process_positions(positions)
	velocities = np.zeros((4, 3), dtype = "int")
	timesteps = 1000
	for t in range(0, timesteps):
		velocities = update_velocities(positions, velocities)
		positions += velocities 
	energy = count_energy(positions, velocities)
	print(f'Total energy is {energy}')

if __name__ == "__main__":
	main()
