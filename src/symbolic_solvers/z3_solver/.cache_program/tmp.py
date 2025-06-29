from z3 import *

people_sort, (Vladimir, Wendy) = EnumSort('people', ['Vladimir', 'Wendy'])
meals_sort, (breakfast, lunch, dinner, snack) = EnumSort('meals', ['breakfast', 'lunch', 'dinner', 'snack'])
foods_sort, (fish, hot_cakes, macaroni, omelet, poached_eggs) = EnumSort('foods', ['fish', 'hot_cakes', 'macaroni', 'omelet', 'poached_eggs'])
people = [Vladimir, Wendy]
meals = [breakfast, lunch, dinner, snack]
foods = [fish, hot_cakes, macaroni, omelet, poached_eggs]
eats = Function('eats', people_sort, meals_sort, foods_sort)

pre_conditions = []
m = Const('m', meals_sort)
pre_conditions.append(ForAll([m], eats(Vladimir, m) != eats(Wendy, m)))
p = Const('p', people_sort)
f = Const('f', foods_sort)
pre_conditions.append(ForAll([p, f], Sum([eats(p, m) == f for m in meals]) <= 1))
p = Const('p', people_sort)
pre_conditions.append(ForAll([p], Or(eats(p, breakfast) == hot_cakes, eats(p, breakfast) == poached_eggs, eats(p, breakfast) == omelet)))
p = Const('p', people_sort)
pre_conditions.append(ForAll([p], Or(eats(p, lunch) == fish, eats(p, lunch) == hot_cakes, eats(p, lunch) == macaroni, eats(p, lunch) == omelet)))
p = Const('p', people_sort)
pre_conditions.append(ForAll([p], Or(eats(p, dinner) == fish, eats(p, dinner) == hot_cakes, eats(p, dinner) == macaroni, eats(p, dinner) == omelet)))
p = Const('p', people_sort)
pre_conditions.append(ForAll([p], Or(eats(p, snack) == fish, eats(p, snack) == omelet)))
pre_conditions.append(eats(Wendy, lunch) == omelet)
m = Const('m', meals_sort)
pre_conditions.append(ForAll([m], eats(Vladimir, m) != eats(Wendy, m)))
p = Const('p', people_sort)
f = Const('f', foods_sort)
pre_conditions.append(ForAll([p, f], Sum([eats(p, m) == f for m in meals]) <= 1))
p = Const('p', people_sort)
pre_conditions.append(ForAll([p], Or(eats(p, breakfast) == hot_cakes, eats(p, breakfast) == poached_eggs, eats(p, breakfast) == omelet)))
p = Const('p', people_sort)
pre_conditions.append(ForAll([p], Or(eats(p, lunch) == fish, eats(p, lunch) == hot_cakes, eats(p, lunch) == macaroni, eats(p, lunch) == omelet)))
p = Const('p', people_sort)
pre_conditions.append(ForAll([p], Or(eats(p, dinner) == fish, eats(p, dinner) == hot_cakes, eats(p, dinner) == macaroni, eats(p, dinner) == omelet)))
p = Const('p', people_sort)
pre_conditions.append(ForAll([p], Or(eats(p, snack) == fish, eats(p, snack) == omelet)))
pre_conditions.append(eats(Wendy, lunch) == omelet)

def is_valid(option_constraints):
    solver = Solver()
    solver.add(pre_conditions)
    solver.add(Not(option_constraints))
    return solver.check() == unsat

def is_unsat(option_constraints):
    solver = Solver()
    solver.add(pre_conditions)
    solver.add(option_constraints)
    return solver.check() == unsat

def is_sat(option_constraints):
    solver = Solver()
    solver.add(pre_conditions)
    solver.add(option_constraints)
    return solver.check() == sat

def is_accurate_list(option_constraints):
    return is_valid(Or(option_constraints)) and all([is_sat(c) for c in option_constraints])

def is_exception(x):
    return not x


m = Const('m', meals_sort)
if is_valid(Exists([m], eats(Vladimir, m) == fish)): print('(A)')
m = Const('m', meals_sort)
if is_valid(Exists([m], eats(Vladimir, m) == hot_cakes)): print('(B)')
m = Const('m', meals_sort)
if is_valid(Exists([m], eats(Vladimir, m) == macaroni)): print('(C)')
m = Const('m', meals_sort)
if is_valid(Exists([m], eats(Vladimir, m) == omelet)): print('(D)')
m = Const('m', meals_sort)
if is_valid(Exists([m], eats(Vladimir, m) == poached_eggs)): print('(E)')