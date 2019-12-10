import math

def create_map(path):
	with open(path, 'r') as f:
		map = f.read().splitlines()
	return(map)

class asteroid():
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.normals = []
		self.angle = None
		self.distance = None

	def add_normal(self, asteroid):
		x = asteroid.x - self.x
		y = asteroid.y - self.y
		norm = (x ** 2 + y ** 2) ** 0.5
		self.normals.append((round(x / norm, 5), round(y / norm, 5)))

	def calculate_visible(self):
		return len(list(set(self.normals)))

	def angle_and_distance(self, cx, cy):
		if (self.x == cx) & (self.y == cy):
			self.angle = -1
			self.distance = 0
		else:
			x = self.x - cx
			y = self.y - cy
			self.angle = round((math.degrees(math.atan2(y, x)) + 90.0) % 360.0, 3)
			self.distance = (x ** 2 + y ** 2) ** 0.5

class galaxy():
	def __init__(self, map):
		self.asteroids = []
		self.rows = len(map)
		self.cols = len(map[0])
		for i, row in enumerate(map):
			for j, val in enumerate(row):
				if val == '#':
					new_asteroid = asteroid(j, i)
					for a in self.asteroids:
						a.add_normal(new_asteroid)
						new_asteroid.add_normal(a)
					self.asteroids.append(new_asteroid)

	def find_best_asteroid(self):
		x = None
		y = None
		val = -1
		for a in self.asteroids:
			if a.calculate_visible() > val:
				x, y, val = (a.x, a.y, a.calculate_visible())
		print(f'Best asteroid at ({x},{y}) with visibility = {val}')
		return(x, y)

	def vaporize_asteroids(self, cx, cy):
		sequence = []
		for ast in self.asteroids:
			ast.angle_and_distance(cx, cy)
			sequence.append([ast.x, ast.y, ast.angle, ast.distance])
		sequence = sorted(sequence, key = lambda x: (x[2], x[3]))[1:]
		inc = []
		acc = 0
		for i, v in enumerate(sequence):
			if i == 0:
				inc.append(0)
			elif sequence[i][2] % 360.0 == sequence[i - 1][2] % 360.0:
				acc += 1.0
				inc.append(acc)
			else:
				acc = 0
				inc.append(acc)
		
		for i, v in enumerate(inc):
			sequence[i][2] = sequence[i][2] + v * 360		
		sequence = sorted(sequence, key = lambda x: (x[2], x[3]))

		for i, s in enumerate(sequence):
			print(f'{i + 1} vaporized: {s}')

	def __str__(self):
		new_map = [[0 for i in range(0, self.cols)] for x in range(0, self.rows)]
		for a in self.asteroids:
			new_map[a.x][a.y] = a.calculate_visible()
		s = ''
		for row in new_map:
			s += str(row) + '\n'	
		return s

def main():
	map = create_map('input.txt')
	print(map)
	gal = galaxy(map)
	print(f'galaxy has {len(gal.asteroids)} asteroids')
	print(gal)
	cx, cy = gal.find_best_asteroid()
	gal.vaporize_asteroids(cx, cy)


if __name__ == "__main__":
	main()