#! /usr/bin/env python
DEBUG = False
DEBUG = True

from sys import argv
from os.path import isfile
import re

import itertools

color_red = '\033[1;31m'
color_blue = '\033[1;34m'
color_green = '\033[1;32m'
color_yellow = '\033[1;33m'
color_normal = '\033[0m'  

"""
Convenciones para pasar output a C:
Cada linea:
<tipo de constraint>
(+|-)[<numero de fact>]{1,2}
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

    def verificar(self, gd = None):
        if gd == None:
            atom = self.gd
        else:
            atom = gd

        predicate_number = names_predicates[atom.predicate]
        predicate_arg_types = predicates_names[predicate_number][1]        
        predicate_arg_list = atom.arguments

        # predicate_arg_types contiene los enteros correspondientes
        # a los tipos del predicado que se esta analizando

        # chequeo del numero de argumentos
        if len(predicate_arg_list) != len(predicate_arg_types):
            raise SystemExit("ERROR: no coincide el numero de argumentos " \
                    + "en el predicado '%s'" %(str(atom)))

        # chequeo del tipo de los argumentos
        variable_types = {}
        for index, arg in enumerate(predicate_arg_list):
            if not variable_types.has_key(arg):
                variable_types[arg] = predicate_arg_types[index]
            else:
                if predicate_arg_types[index] != variable_types[arg]:
                    # error de tipo
                    raise SystemExit("ERROR: no coincide el tipo de los argumentos " \
                            + "en el predicado '%s', en el argumento numero %s" \
                            %(str(atom), index+1))

    def add_constraint(self):
        predicate_arg_list = self.gd.arguments
        self.instantiate(0, len(predicate_arg_list))

    def instantiate(self, argument_index, max_level):
        atom = self.gd
        predicate_number = names_predicates[atom.predicate]
        predicate_arg_types = predicates_names[predicate_number][1]        
        predicate_arg_list = atom.arguments
        # predicate_arg_types contiene los enteros correspondientes
        # a los tipos del predicado que se esta analizando
        if argument_index == max_level:
            if isinstance(self.gd, Not):
                instantiated_constraints.append([self.name, '-' ,"(" + \
                        " ".join([atom.predicate] + predicate_arg_list) + ")"]) 
            else:
                instantiated_constraints.append([self.name, '+', "(" + \
                        " ".join([atom.predicate] + predicate_arg_list) + ")"]) 
        else:
            # si ya hay una constante, continuar al siguiente argumento
            if is_instantiated(predicate_arg_list[argument_index]):
                self.instantiate(argument_index + 1, max_level)
            else:
                constants_of_this_type = \
                        types_names[predicate_arg_types[argument_index]][1]
                for constant in constants_of_this_type:
                    variables_instantiated = \
                            [(argument_index, predicate_arg_list[argument_index])]
                    for j in range(argument_index + 1, max_level):
                        # chequear argumentos repetidos
                        if predicate_arg_list[j] == predicate_arg_list[argument_index]:
                            variables_instantiated.append((j, predicate_arg_list[j]))
                            predicate_arg_list[j] = constants_names[constant]
                    predicate_arg_list[argument_index] = constants_names[constant] # instantiate
                    #print predicate_arg_list
                    self.instantiate(argument_index + 1, max_level)
                    for index, var in variables_instantiated:
                        predicate_arg_list[index] = var # des-instanciar las variables

class BinaryConstraint(Constraint):
    def __init__(self, name, gd, gd2):
        Constraint.__init__(self, name, gd)

        self.gd2 = gd2

    def __str__(self):
        return Constraint.__str__(self) + ", " +\
               str(self.gd2)

    def verificar(self, gd = None):
        Constraint.verificar(self, self.gd)
        Constraint.verificar(self, self.gd2)

    def add_constraint(self):
        predicate_arg_list = self.gd.arguments
        predicate_arg_list2 = self.gd2.arguments

        binary_constraints, binary_constraints2 = [], []

        self.instantiate(self.gd, 0, len(predicate_arg_list), binary_constraints)
        self.instantiate(self.gd2, 0, len(predicate_arg_list2), binary_constraints2)
       
        if isinstance(self.gd, Not): sign = "-"
        else: sign = "+"
        if isinstance(self.gd2, Not): sign2 = "-"
        else: sign2 = "+"

        for p in itertools.product(binary_constraints, binary_constraints2):
            instantiated_constraints.append([self.name, sign, p[0], sign2, p[1]])
        
    def instantiate(self, gd, argument_index, max_level, constraints_generated):
        atom = gd
        predicate_number = names_predicates[atom.predicate]
        predicate_arg_types = predicates_names[predicate_number][1]        
        predicate_arg_list = atom.arguments
        # predicate_arg_types contiene los enteros correspondientes
        # a los tipos del predicado que se esta analizando
        if argument_index == max_level:
            constraints_generated.append("(" + \
                    " ".join([atom.predicate] + predicate_arg_list) + ")") 
        else:
            # si ya hay una constante, continuar al siguiente argumento
            if is_instantiated(predicate_arg_list[argument_index]):
                self.instantiate(gd, argument_index + 1, max_level, constraints_generated)
            else:
                constants_of_this_type = \
                        types_names[predicate_arg_types[argument_index]][1]
                for constant in constants_of_this_type:
                    variables_instantiated = \
                            [(argument_index, predicate_arg_list[argument_index])]
                    for j in range(argument_index + 1, max_level):
                        # chequear argumentos repetidos

                        if predicate_arg_list[j] == predicate_arg_list[argument_index]:
                            variables_instantiated.append((j, predicate_arg_list[j]))
                            predicate_arg_list[j] = constants_names[constant]
                    predicate_arg_list[argument_index] = constants_names[constant] # instantiate
                    #print predicate_arg_list
                    self.instantiate(gd, argument_index + 1, max_level, constraints_generated)
                    for index, var in variables_instantiated:
                        predicate_arg_list[index] = var # des-instanciar las variables           

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

def is_instantiated(variable):
    return not isinstance(variable, str) or variable[0] != "?"

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
                                   + "(\([^)]+\)|\(not\s*\([^)]+\)\s*\))\s*"
                                   + "(\([^)]+\)|\(not\s*\([^)]+\)\s*\))\s*\)")

    unary_list = unary_constraints.findall(constraints_string)
    binary_list = binary_constraints.findall(constraints_string)

    # se verifica que si existen constantes en las listas
    # de constraints, estas se correspondan a alguna
    # constante del problema o dominio

    # esta agregacion de constraints sirve solo para casos sencillos
    # (not y formulas atomicas), este manejo se hace para
    # evitar analizar la gramatica
    constraints_list = []
    try:
        for c in unary_list:
            constraint_name = c[0]
            atom = c[1].replace('(',' ').replace(')',' ').split()

            if atom[0] == "not":
                check_constants(atom[1:])
                constraints_list.append(Constraint(constraint_name, \
                        Not(atom[1].upper(), atom[2:])))
            else:
                check_constants(atom)
                constraints_list.append(Constraint(constraint_name, \
                        AtomicFormula(atom[0].upper(), atom[1:])))
        for c in binary_list:
            constraint_name = c[0]
            atom = c[1].replace('(',' ').replace(')',' ').split()
            atom2 = c[2].replace('(',' ').replace(')',' ').split()

            if atom[0] == "not" and atom2[0] == "not":
                check_constants(atom[1:])
                check_constants(atom2[1:])
                constraints_list.append(BinaryConstraint(constraint_name, \
                        Not(atom[1].upper(), atom[2:]),\
                        Not(atom2[1].upper(), atom2[2:])))
            elif atom[0] != "not" and atom2[0] == "not":
                check_constants(atom)
                check_constants(atom2[1:])
                constraints_list.append(BinaryConstraint(constraint_name, \
                        AtomicFormula(atom[0].upper(), atom[1:]),\
                        Not(atom2[1].upper(), atom2[2:])))
            elif atom[0] == "not" and atom2[0] != "not":
                check_constants(atom[2:])
                check_constants(atom2)
                constraints_list.append(BinaryConstraint(constraint_name, \
                        Not(atom[1].upper(), atom[2:]),\
                        AtomicFormula(atom2[0].upper(), atom2[1:])))
            else:
                check_constants(atom)
                check_constants(atom2)
                constraints_list.append(BinaryConstraint(constraint_name, \
                        AtomicFormula(atom[0].upper(), atom[1:]),\
                    AtomicFormula(atom2[0].upper(), atom2[1:])))
    except KeyError, e:
        raise SystemExit("ERROR: no se pudo encontrar el predicado %s" %(str(e)))

    return constraints_list    

def check_constants(variable_list):
    # en variable_list[0] esta el nombre del predicado
    # en el resto de la lista estan las variables
    for index, variable in enumerate(variable_list[1:]):
        if is_instantiated(variable):
            constant = variable.upper()
            try:
                constant_number = names_constants[constant]
            except KeyError:
                raise SystemExit("ERROR: no se pudo encontrar la constante '%s'" %(variable))
            # obtener el tipo esperado por el predicado
            predicate_number = names_predicates[variable_list[0].upper()]
            expected_type = predicates_names[predicate_number][1][index]

            if constant_number not in types_names[expected_type][1]:
                raise SystemExit("ERROR: la constante '%s' deberia ser de tipo '%s'"\
                        % (constant, types_names[expected_type][0]))

# main
# se lee el dominio
try:
    f = open(argv[1], 'r')
    dominio = f.read()
    f.close()
except IndexError:
    raise SystemExit("No hay archivo de dominio de entrada")
except IOError:
    raise SystemExit("No se encontro el archivo de dominio")

# se separa la seccion de constraints del PDDL
primero = dominio.partition("(:constraints") 
segundo = primero[2].partition("(:action") 

constraints_string = segundo[0]

no_constraints = primero[0] + segundo[1] + segundo[2] 

# se reescribe el archivo sin constraints
archivo_dominio = argv[1].partition(".")
nombre_nuevo = archivo_dominio[0] + "_nc" + archivo_dominio[1] +\
        archivo_dominio[2]

if not isfile(nombre_nuevo):
    archivo_nuevo = open(nombre_nuevo, 'w')
    archivo_nuevo.write(no_constraints)
    archivo_nuevo.close()
    if DEBUG: print ">>> se escribio un archivo nuevo " + nombre_nuevo   

# se lee el problema
try:
    f = open(argv[2], 'r')
    problema = f.read()
    f.close()
except IndexError:
    raise SystemExit("No hay archivo de problema de entrada")
except IOError:
    raise SystemExit("No se encontro el archivo de problema")

# se separa la seccion de constraints del PDDL
primero = problema.partition("(:constraints") 

constraints_string += " " + primero[2]

if primero[2] == '':
    # no hay constraints en el archivo
    no_constraints = primero[0]
else:
    no_constraints = primero[0] + " " + ")\n"

# se reescribe el archivo sin constraints
archivo_problema = argv[2].partition(".")
nombre_nuevo = archivo_problema[0] + "_nc" + archivo_problema[1] +\
        archivo_problema[2]

if not isfile(nombre_nuevo):
    archivo_nuevo = open(nombre_nuevo, 'w')
    archivo_nuevo.write(no_constraints)
    archivo_nuevo.close()
    if DEBUG: print ">>> se escribio un archivo nuevo " + nombre_nuevo   

# quitar comentarios
lines = constraints_string.splitlines()
for i, line in enumerate(lines):
    lines[i] = line.partition(";")[0]
constraints_string = " ".join(lines)

# se lee el archivo de tablas pasado por el planificador
try:
    f = open(argv[3], 'r')
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

# constraints instanciados, lista global
instantiated_constraints = []

get_maps()

if DEBUG:
    print color_red + "\nTIPOS DE CADA CONSTANTE: " + color_normal
    print type_of_constant

constraints_list = get_constraints(constraints_string)

for c in constraints_list:
    c.verificar()

for c in constraints_list:
    c.add_constraint()

output = open("constraints", 'w')
for index, elem in enumerate(instantiated_constraints):
    try:
        if len(elem) == 3:
            output.write(str(constraint_type[elem[0]]) +\
                " " + elem[1] + " " + str(names_facts[elem[2]]) +"\n")
        else: # len(elem) == 5
            output.write(str(constraint_type[elem[0]]) +\
                " " + elem[1] + " " + str(names_facts[elem[2]]) + " " +\
                elem[3] + " " + str(names_facts[elem[4]]) +"\n")
    except KeyError:
        print "No se pudo procesar el constraint %s" %(" ".join(elem))
output.close()
print "Constraints generados"

#print instantiated_constraints
#print len(instantiated_constraints)
