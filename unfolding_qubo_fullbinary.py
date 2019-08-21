#!/usr/bin/env python3

import os
import sys
import argparse
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt
from decimal2binary import *
import dimod

np.set_printoptions(precision=1, linewidth=200, suppress=True)

parser = argparse.ArgumentParser("Quantum unfolding")
parser.add_argument('-l', '--lmbd', default=0.00)
args = parser.parse_args()

# truth-level:
x = [5, 10, 3]

# response matrix:
R = [[3, 1, 0], [1, 3, 1], [0, 1, 2]]

# pseudo-data:
d = [32, 40, 15]

# convert to numpy arrays
x = np.array(x, dtype='uint8')
R = np.array(R, dtype='uint8')
b = np.array(d, dtype='uint8')

# closure test
b = np.dot(R, x)

n = 4
N = x.shape[0]

print("INFO: N bins:", N)
print("INFO: n-bits encoding:", n)

lmbd = np.uint8(args.lmbd)  # regularization strength
D = laplacian(N)

# convert to bits
x_b = discretize_vector(x, n)
b_b = discretize_vector(b, n)
R_b = d2b(R, n)
D_b = d2b(D, n)

print("INFO: Truth-level x:")
print(x, x_b)
print("INFO: pseudo-data b:")
print(b, b_b)
print("INFO: Response matrix:")
print(R)
print(R_b)
print("INFO: Laplacian operator:")
print(D)
print(D_b)
print("INFO: regularization strength:", lmbd)

# Create QUBO operator

# linear constraints
h = np.zeros(N)
for j in range(N):
    idx = (j)
    h[idx] = 0
    for i in range(N):
        h[idx] += (R[i][j]*R[i][j] -
                   2*R[i][j] * b[i] +
                   lmbd*D[i][j]*D[i][j])
    #print("h", idx, ":", h[idx])

# quadratic constraints
J = np.zeros([N, N])
for j in range(N):
    for k in range(j+1, N):
        idx = (j, k)
        J[idx] = 0
        for i in range(N):
            J[idx] += 2*(R[i][j]*R[i][k] + lmbd*D[i][j]*D[i][k])
        #print("J", idx, ":", J[idx])

print("h:")
print(h)
print("J:")
print(J)

h_b = discretize_vector(h, n)
J_b = d2b(J, n)

print("h_b:")
print(h_b)
print("J_b:")
print(J_b)

# QUBO
bqm = dimod.BinaryQuadraticModel(linear=h,
                                 quadratic=J,
                                 offset=0.0,
                                 vartype=dimod.BINARY)
print("INFO: solving the QUBO model...")
result = dimod.ExactSolver().sample(bqm)
print("INFO: ...done.")

energy_min = 1e15
q = None
for sample, energy in result.data(['sample', 'energy']):
    #print(sample, energy)

    if energy > energy_min:
        continue
    energy_min = energy
    q = list(sample.values())

q = np.array(q)
y = compact_vector(q, n)
print("INFO: best-fit:   ", q, "::", y, ":: E =", energy_min)
print("INFO: truth value:", x_b, "::", x)
