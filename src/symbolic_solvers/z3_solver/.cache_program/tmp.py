from z3 import *

children_sort, (Fred, Juan, Marc, Paul, Nita, Rachel, Trisha) = EnumSort('children', ['Fred', 'Juan', 'Marc', 'Paul', 'Nita', 'Rachel', 'Trisha'])
lockers_sort = IntSort()
children = [Fred, Juan, Marc, Paul, Nita, Rachel, Trisha]
lockers = [1, 2, 3, 4, 5]
assigned = Function('assigned', children_sort, lockers_sort)
shared = Function('shared', lockers_sort, BoolSort())

pre_conditions = []
c = Const('c', children_sort)
pre_conditions.append(ForAll([c], Or([assigned(c) == l for l in lockers])))
c = Const('c', children_sort)
c1 = Const('c1', children_sort)
c2 = Const('c2', children_sort)
pre_conditions.append(And([Or(Exists([c], assigned(c) == l), Exists([c1, c2], And(c1 != c2, assigned(c1) == l, assigned(c2) == l, shared(l)))) for l in lockers]))
b = Const('b', children_sort)
g = Const('g', children_sort)
pre_conditions.append(And([Implies(shared(l), Exists([b, g], And(assigned(b) == l, assigned(g) == l, Or(b == Fred, b == Juan, b == Marc, b == Paul), Or(g == Nita, g == Rachel, g == Trisha)))) for l in lockers]))
pre_conditions.append(Or([And(assigned(Juan) == l, shared(l)) for l in lockers]))
pre_conditions.append(And([Implies(assigned(Rachel) == l, Not(shared(l))) for l in lockers]))
pre_conditions.append(And([Implies(Or(assigned(Nita) == l, assigned(Trisha) == l), Not(Or(assigned(Nita) == l+1, assigned(Nita) == l-1, assigned(Trisha) == l+1, assigned(Trisha) == l-1))) for l in lockers]))
pre_conditions.append(assigned(Fred) == 3)
b = Const('b', children_sort)
b = Const('b', children_sort)
pre_conditions.append(And(Exists([b], And(assigned(b) == 1, Or(b == Fred, b == Juan, b == Marc, b == Paul), Not(shared(1)))), Exists([b], And(assigned(b) == 2, Or(b == Fred, b == Juan, b == Marc, b == Paul), Not(shared(2))))))
c0 = Const('c0', children_sort)
pre_conditions.append(ForAll([c0], And(1 <= assigned(c0), assigned(c0) <= 5)))
c = Const('c', children_sort)
pre_conditions.append(ForAll([c], Or([assigned(c) == l for l in lockers])))
c = Const('c', children_sort)
c1 = Const('c1', children_sort)
c2 = Const('c2', children_sort)
pre_conditions.append(And([Or(Exists([c], assigned(c) == l), Exists([c1, c2], And(c1 != c2, assigned(c1) == l, assigned(c2) == l, shared(l)))) for l in lockers]))
b = Const('b', children_sort)
g = Const('g', children_sort)
pre_conditions.append(And([Implies(shared(l), Exists([b, g], And(assigned(b) == l, assigned(g) == l, Or(b == Fred, b == Juan, b == Marc, b == Paul), Or(g == Nita, g == Rachel, g == Trisha)))) for l in lockers]))
pre_conditions.append(Or([And(assigned(Juan) == l, shared(l)) for l in lockers]))
pre_conditions.append(And([Implies(assigned(Rachel) == l, Not(shared(l))) for l in lockers]))
pre_conditions.append(And([Implies(Or(assigned(Nita) == l, assigned(Trisha) == l), Not(Or(assigned(Nita) == l+1, assigned(Nita) == l-1, assigned(Trisha) == l+1, assigned(Trisha) == l-1))) for l in lockers]))
pre_conditions.append(assigned(Fred) == 3)
b = Const('b', children_sort)
b = Const('b', children_sort)
pre_conditions.append(And(Exists([b], And(assigned(b) == 1, Or(b == Fred, b == Juan, b == Marc, b == Paul), Not(shared(1)))), Exists([b], And(assigned(b) == 2, Or(b == Fred, b == Juan, b == Marc, b == Paul), Not(shared(2))))))

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


if is_sat(assigned(Juan) == 4): print('(A)')
if is_sat(assigned(Paul) == 4): print('(B)')
if is_sat(assigned(Rachel) == 4): print('(C)')
if is_sat(And(assigned(Juan) == 4, assigned(Nita) == 4, shared(4))): print('(D)')
if is_sat(And(assigned(Marc) == 4, assigned(Trisha) == 4, shared(4))): print('(E)')