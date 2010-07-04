#! /usr/bin/env python
DEBUG = False
DEBUG = True

from sys import argv
from os.path import isfile
import re

color_red = '\033[1;31m'
color_blue = '\033[1;34m'
color_green = '\033[1;32m'
color_yellow = '\033[1;33m'
color_normal = '\033[0m'  

class Constraint:
    def __init__(self, name, gd):
        self.name = name
        self.gd = gd

    def __str__(self):
        return "Constraint " + color_red + self.name + color_normal +\
                " " + str(self.gd)

class BinaryConstraint(Constraint):
    def __init__(self, name, gd, gd2):
        Constraint.__init__(self, name, gd)
        self.gd2 = gd2

    def __str__(self):
        return Constraint.__str__(self) + ", " +\
               str(self.gd2)

class AtomicFormula:
    def __init__(self, predicate, arguments):
        self.predicate = predicate
        self.arguments = arguments

    def __str__(self):
        return color_green + self.predicate + color_normal + " " +\
                str(self.arguments)

class Not:
    def __init__(self, gd):
        self.gd = gd

    def __str__(self):
        return "Not " + str(self.gd)

try:
    f = open(argv[1], 'r')
    original = f.read()
    f.close()
except IndexError:
    raise SystemExit("No hay archivo de entrada")
except IOError:
    raise SystemExit("No se encontro el archivo")

primero = original.partition("(:constraints") 
segundo = primero[2].partition("(:action") 

constraints = segundo[0]

no_constraints = primero[0] + segundo[1] + segundo[2] 

# se reescribe el archivo sin constraints
archivo_original = argv[1].partition(".")
nombre_nuevo = archivo_original[0] + "_nc" + archivo_original[1] +\
        archivo_original[2]

if not isfile(nombre_nuevo):
    archivo_nuevo = open(nombre_nuevo, 'w')
    archivo_nuevo.write(no_constraints)
    archivo_nuevo.close()
    if DEBUG: print ">>> wrote new file " + nombre_nuevo

# strip comments
lines = constraints.splitlines()
for i, line in enumerate(lines):
    lines[i] = line.partition(";")[0]
constraints = " ".join(lines)

try:
    f = open(argv[2], 'r')
    tablas = f.read()
    f.close()
except IndexError:
    try:
        f = open("tablas", 'r')
        tablas = f.read().split("\n\n")
        f.close()
    except IOError:
        raise SystemExit("No se encontro el archivo de tablas")
except IOError:
    raise SystemExit("No se encontro el archivo de tablas")

# maps
constants_names = []
names_constants = {}
for line in tablas[0].splitlines()[1:]:
    partition = line.split()
    constants_names.append(partition[1])
    names_constants[partition[1]] = int(partition[0])

print constants_names, names_constants

types_names = []
names_types = {}
for line in tablas[1].splitlines()[1:]:
    partition = line.split(" ", 2)
    # convert to int the list of vars of every type
    variable_list = line.split()[2:]
    for i, var in enumerate(variable_list):
        variable_list[i] = int(var)

    types_names.append((partition[1], variable_list))
    names_types[partition[1]] = int(partition[0])

print
print types_names, names_types

predicates_names = []
names_predicates = {}
for line in tablas[2].splitlines()[1:]:
    partition = line.split()
    predicates_names.append(partition[1])
    names_predicates[partition[1]] = int(partition[0])

print
print predicates_names, names_predicates

facts_names = []
names_facts = {}
for line in tablas[3].splitlines()[1:]:
    partition = line.split(" ", 1)
    facts_names.append(partition[1])
    names_facts[partition[1]] = int(partition[0])

print
print facts_names, names_facts

# parsear el string "constraints" en este punto
# si se quiere agregar constraints mas elaboradas
unary_constraints = re.compile(r"\((at end|at-most-once|always|sometime)\b\s+"\
                               + "(\([^)]+\))\)")
binary_constraints = re.compile(r"\((sometimes-before|sometimes-after)\b\s+"\
                               + "(\([^)]+\))\s+(\([^)]+\))\)")

unary_list = unary_constraints.findall(constraints)
binary_list = binary_constraints.findall(constraints)

# esta agregacion de constraints sirve solo para casos sencillos
# (not y formulas atomicas), este manejo se hace para
# evitar analizar la gramatica
constraints_list = []
for c in unary_list:
    constraint_name = c[0]
    atom = c[1].replace('(',' ').replace(')',' ').split()
    if atom[0] == "not":
        constraints_list.append(Constraint(constraint_name, \
                Not(AtomicFormula(atom[1], atom[2:]))))
    else:
        constraints_list.append(Constraint(constraint_name, \
                AtomicFormula(atom[0], atom[1:])))
for c in binary_list:
    constraint_name = c[0]
    atom = c[1].replace('(',' ').replace(')',' ').split()
    atom2 = c[2].replace('(',' ').replace(')',' ').split()
    if atom[0] == "not" and atom2[0] == "not":
        constraints_list.append(BinaryConstraint(constraint_name, \
                Not(AtomicFormula(atom[1], atom[2:]),\
                Not(AtomicFormula(atom2[1], atom2[2:])))))
    elif atom[0] != "not" and atom2[0] == "not":
        constraints_list.append(BinaryConstraint(constraint_name, \
                AtomicFormula(atom[0], atom[1:]),\
                Not(AtomicFormula(atom2[1], atom2[2:]))))
    elif atom[0] == "not" and atom2[0] != "not":
        constraints_list.append(BinaryConstraint(constraint_name, \
                Not(AtomicFormula(atom[1], atom[2:]),\
                AtomicFormula(atom2[0], atom2[1:]))))
    else:
        constraints_list.append(BinaryConstraint(constraint_name, \
                Not(AtomicFormula(atom[0], atom[1:])),\
                Not(AtomicFormula(atom2[0], atom2[1:]))))

#for c in constraints_list:
#    print c

