import pyhop
import json

def check_enough (state, ID, item, num):
	if getattr(state,item)[ID] >= num: return []
	return False

def produce_enough (state, ID, item, num):
	return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods ('have_enough', check_enough, produce_enough)

def produce (state, ID, item):
	return [('produce_{}'.format(item), ID)]

pyhop.declare_methods ('produce', produce)

def make_method(name, rule):
	def method(state, ID):
		tasks = []

		if 'Requires' in rule:
			for item, amount in rule['Requires'].items():
				tasks.append(('have_enough', ID, item, amount))

		if 'Consumes' in rule:
			for item, amount in rule['Consumes'].items():
				tasks.append(('have_enough', ID, item, amount))

		tasks.append(('op_' + name, ID))
		return tasks
	
	method.__name__ = 'produce_{}'.format(name.replace(' ', '_'))
	return method

def declare_methods (data):
	# some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first

	# your code here
	# hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)	
	methods = {}
	recipes = sorted(data['Recipes'].items(), key=lambda item: item[1]['Time'])

	for name, rule in recipes:
		method = make_method(name.replace(' ', '_'), rule)
		for item in rule['Produces']:
			if item not in methods:
				methods[item] = []	
			methods[item].append(method)
	
	for item, mlist in methods.items():
		pyhop.declare_methods('produce_{}'.format(item), *mlist)

def make_operator (rule):
	recipe_name, details = rule
	def operator (state, ID):
		# your code here
		time = details['Time']
		if state.time[ID] < time: return False

		reqs = details.get('Requires', {}) # Required items
		cons = details.get('Consumes', {}) # Consumables 
		prod = details.get('Produces', {}) # Produced items

		# Check if we have enough  
		if reqs and not all(getattr(state, item)[ID] >= num for item, num in reqs.items()):
			return False
		
		if cons and not all(getattr(state, item)[ID] >= num for item, num in cons.items()):
			return False
		
		for item, num in prod.items():
			getattr(state, item)[ID] += num

		for item, num in cons.items():
			getattr(state, item)[ID] -= num

		state.time[ID] -= time
		return state

	operator.__name__ = 'op_{}'.format(recipe_name.replace(' ', '_'))
	return operator

def declare_operators (data):
	# your code here
	recipes = data['Recipes']
	operators = [make_operator((recipe_name, details)) for recipe_name, details in recipes.items()]
	pyhop.declare_operators(*operators)

def add_heuristic(data, ID):
    # prune search branch if heuristic() returns True
    # do not change parameters to heuristic(), but can add more heuristic functions with the same parameters:
    # e.g. def heuristic2(...); pyhop.add_check(heuristic2)
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        if state.time[ID] < 1:
            return True

        if depth > 10:
            return True

        return False

    pyhop.add_check(heuristic)

def set_up_state (data, ID, time=0):
	state = pyhop.State('state')
	state.time = {ID: time}

	for item in data['Items']:
		setattr(state, item, {ID: 0})

	for item in data['Tools']:
		setattr(state, item, {ID: 0})

	for item, num in data['Initial'].items():
		setattr(state, item, {ID: num})

	return state

def set_up_goals (data, ID):
	goals = []
	for item, num in data['Goal'].items():
		goals.append(('have_enough', ID, item, num))

	return goals

if __name__ == '__main__':
	rules_filename = 'crafting.json'

	with open(rules_filename) as f:
		data = json.load(f)

	state = set_up_state(data, 'agent', time=300) # allot time here
	goals = set_up_goals(data, 'agent')

	declare_operators(data)
	declare_methods(data)
	add_heuristic(data, 'agent')

	# pyhop.print_operators()
	# pyhop.print_methods()

	# Hint: verbose output can take a long time even if the solution is correct; 
	# try verbose=1 if it is taking too long
	pyhop.pyhop(state, goals, verbose=1)
	# pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)
