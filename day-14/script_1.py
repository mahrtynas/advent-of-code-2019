import math

def get_reactions(path):
	reactions = dict()
	with open(path, 'r') as f:
		file_lines = f.readlines()
	for line in file_lines:
		line_parts = line.split("=>")
		target = line_parts[1].strip("\n| ")
		inputs = [x.strip(" ") for x in line_parts[0].split(",")]
		reactions[target] = inputs
	return reactions

def parse_value(value):
	[val, name] = value.split(" ")
	val = int(val)
	return name, val

class Element():
	def __init__(self, name, min_value):
		self.name = name
		self.min_value = int(min_value)
		self.dependent_elements = []
		self.dependent_amounts = []
		self.available = 0
		self.demand = 0
	
	def __str__(self):
		return (f'Info about element {self.name}:\n'
			f'Dependents: {[x.name for x in self.dependent_elements]}\n'
			f'Dependent amounts: {self.dependent_amounts}\n'
			f'Demand: {self.demand}\n'
			f'Available: {self.available}')

	def assign_dependents(self, de, value):
		self.dependent_elements.append(de)
		self.dependent_amounts.append(value)

	def produce(self, requested_amount):
		self.demand += requested_amount
		if self.available >= requested_amount:
			self.available -= requested_amount
		else:
			additional = requested_amount - self.available
			production_quantity = math.ceil(additional / self.min_value)
			if self.name != "ORE":
				for i, elem in enumerate(self.dependent_elements):
					elem.produce(production_quantity * self.dependent_amounts[i])
			self.available += production_quantity * self.min_value
			self.available -= requested_amount

def main():
	reactions = get_reactions("input.txt")
	elements = dict(ORE = Element('ORE', 1))

	# initiate all elements
	print(reactions)
	for target in reactions:
		name, val = parse_value(target)
		elements[name] = Element(name, val)
	for react in reactions.items():
		el_name, val = parse_value(react[0])
		for i in react[1]:
			name, val = parse_value(i)
			elements[el_name].assign_dependents(elements[name], val)

	elements['FUEL'].produce(191)
	print(elements['ORE'])
	

if __name__ == "__main__":
	main()