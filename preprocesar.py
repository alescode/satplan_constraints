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
        return "Constraint " + color_red + self.name + " " +\
                color_green + self.gd + color_normal

class BinaryConstraint(Constraint):
    def __init__(self, name, gd, gd2):
        Constraint.__init__(self, name, gd)
        self.gd2 = gd2

    def __str__(self):
        return Constraint.__str__(self) + ", " +\
                color_green + self.gd2 + color_normal

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

unary_constraints = re.compile(r"\((at end|at-most-once|always|sometime)\b\s+"\
                               + "(\(.+\))\)")
binary_constraints = re.compile(r"\((sometimes-before|sometimes-after)\b\s+"\
                               + "(\([^)]+\))\s+(\([^)]+\))\)")

unary_list = unary_constraints.findall(constraints)
binary_list = binary_constraints.findall(constraints)

constraints_list = []
for c in unary_list:
    constraints_list.append(Constraint(c[0], c[1]))
for c in binary_list:
    constraints_list.append(BinaryConstraint(c[0], c[1], c[2]))

for c in constraints_list:
    print c

