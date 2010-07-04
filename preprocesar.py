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

"""
Convenciones para pasar output a C:
Cada linea:
<# de elementos en el constraint> <tipo de constraint>
[<numero de fact> (negativo si es not)]{1,2}
"""

constraint_type = {"at end" : 0, "always" : 1, "sometime" : 2, 
        "at-most-once" : 3, "sometimes-after" : 4, "sometimes-before" : 5}

class Constraint:
    def __init__(self, name, gd):
        self.number = len(gd.arguments) + 2
        self.name = name
        self.gd = gd

    def __str__(self):
        return "Constraint " + color_red + str(self.name) + color_normal +\
                " " + str(self.gd)

    def instanciate(self):
        print self.number, constraint_type[self.name], \
                names_predicates[self.gd.predicate]

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
        return color_green + str(self.predicate) + color_normal + " " +\
                str(self.arguments)

class Not(AtomicFormula):

    def __str__(self):
        return "Not " + AtomicFormula.__str__(self)

def get_maps():
    # se crean las asociaciones de constantes, tipos, predicados y hechos
    for line in tablas[0].splitlines()[1:]:
        partition = line.split()
        constants_names.append(partition[1])
        names_constants[partition[1]] = int(partition[0])
                                                                
    if DEBUG:
        print color_red + "\nCONSTANTES " + color_normal
        print constants_names, names_constants

    for line in tablas[1].splitlines()[1:]:
        partition = line.split(" ", 2)
        # se convierten a entero todas las constantes
        constant_list = line.split()[2:]
        for i, const in enumerate(constant_list):
            constant_list[i] = int(const)
            type_of_constant[constant_list[i]] = int(partition[0]) 

        types_names.append((partition[1], constant_list))
        names_types[partition[1]] = int(partition[0])

    if DEBUG:
        print color_red + "\nTIPOS " + color_normal
        print types_names, names_types

    for line in tablas[2].splitlines()[1:]:
        partition = line.split(" ", 2)
        argument_types = line.split()[2:]
        for i, const in enumerate(argument_types):
            argument_types[i] = int(const)

        predicates_names.append((partition[1], argument_types))
        names_predicates[partition[1]] = int(partition[0])

    if DEBUG:
        print color_red + "\nPREDICADOS " + color_normal
        print predicates_names, names_predicates

    for line in tablas[3].splitlines()[1:]:
        partition = line.split(" ", 1)
        facts_names.append(partition[1])
        names_facts[partition[1]] = int(partition[0])

    if DEBUG:
        print color_red + "\nHECHOS " + color_normal
        print facts_names, names_facts

def get_constraints(constraints_string):
    # parsear el string "constraints" en este punto
    # si se quiere agregar constraints mas elaboradas
    unary_constraints = re.compile(r"\((at end|at-most-once|always|sometime)\b\s+"\
                                   + "(\([^)]+\))\)")
    binary_constraints = re.compile(r"\((sometimes-before|sometimes-after)\b\s+"\
                                   + "(\([^)]+\))\s+(\([^)]+\))\)")

    unary_list = unary_constraints.findall(constraints_string)
    binary_list = binary_constraints.findall(constraints_string)

    # esta agregacion de constraints sirve solo para casos sencillos
    # (not y formulas atomicas), este manejo se hace para
    # evitar analizar la gramatica
    constraints_list = []
    try:
        for c in unary_list:
            constraint_name = c[0]
            atom = c[1].replace('(',' ').replace(')',' ').split()
            if atom[0] == "not":
                constraints_list.append(Constraint(constraint_name, \
                        Not(atom[1].upper(), atom[2:])))
            else:
                constraints_list.append(Constraint(constraint_name, \
                        AtomicFormula(atom[0].upper(), atom[1:])))
        for c in binary_list:
            constraint_name = c[0]
            atom = c[1].replace('(',' ').replace(')',' ').split()
            atom2 = c[2].replace('(',' ').replace(')',' ').split()
            if atom[0] == "not" and atom2[0] == "not":
                constraints_list.append(BinaryConstraint(constraint_name, \
                        Not(atom[1].upper(), atom[2:])),\
                        Not(atom2[1].upper(), atom2[2:]))
            elif atom[0] != "not" and atom2[0] == "not":
                constraints_list.append(BinaryConstraint(constraint_name, \
                        AtomicFormula(atom[0].upper(), atom[1:]),\
                        Not(atom2[1].upper(), atom2[2:])))
            elif atom[0] == "not" and atom2[0] != "not":
                constraints_list.append(BinaryConstraint(constraint_name, \
                        Not(atom[1].upper(), atom[2:])),\
                        AtomicFormula(atom2[0].upper(), atom2[1:]))
            else:
                constraints_list.append(BinaryConstraint(constraint_name, \
                        Not(atom[0].upper(), atom[1:]),\
                    Not(atom2[0].upper(), atom2[1:])))
    except KeyError, e:
        raise SystemExit("ERROR: no se pudo encontrar el predicado %s" %(str(e)))

    return constraints_list    

# main
try:
    f = open(argv[1], 'r')
    original = f.read()
    f.close()
except IndexError:
    raise SystemExit("No hay archivo de entrada")
except IOError:
    raise SystemExit("No se encontro el archivo")

# se separa la seccion de constraints del PDDL
primero = original.partition("(:constraints") 
segundo = primero[2].partition("(:action") 

constraints_string = segundo[0]

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

# quitar comentarios
lines = constraints_string.splitlines()
for i, line in enumerate(lines):
    lines[i] = line.partition(";")[0]
constraints_string = " ".join(lines)

# se lee el archivo de tablas pasado por el planificador
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

# maps con las asociaciones, globales
constants_names , types_names , predicates_names , facts_names = [], [], [], []
names_constants , names_types , names_predicates , names_facts = {}, {}, {}, {}

# map que asocia a cada constante su tipo
type_of_constant = {}

get_maps()

if DEBUG:
    print color_red + "\nTIPOS DE CADA CONSTANTE: " + color_normal
    print type_of_constant

constraints_list = get_constraints(constraints_string)

print "\nCONSTRAINTS:"
for c in constraints_list:
    print c
    print "\nnum_elementos, tipo, predicado, variables" 
    instancias = c.instanciate()
