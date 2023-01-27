# This code is from previous work at https://github.com/GabrielPontolillo/Quantum_Algorithm_Implementations
import warnings
import pandas as pd
import math
from math import pi, sqrt, sin, cos
import numpy as np
import scipy.stats as sci
from collections.abc import Callable

from statsmodels.stats.proportion import proportions_ztest

from qiskit import execute, Aer
backend = Aer.get_backend('aer_simulator')

from qiskit.circuit import ClassicalRegister

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)



def assert_equal(circuit_1, qubit_register_1, circuit_2, qubit_register_2, measurements=10000):
    circuit_1.add_register(ClassicalRegister(1))
    c1z = measure_z(circuit_1.copy(), [qubit_register_1])
    c1x = measure_x(circuit_1.copy(), [qubit_register_1])
    c1y = measure_y(circuit_1.copy(), [qubit_register_1])
    z_counts_1 = execute(c1z, backend, shots=measurements, memory=True).result().get_counts()
    x_counts_1 = execute(c1x, backend, shots=measurements, memory=True).result().get_counts()
    y_counts_1 = execute(c1y, backend, shots=measurements, memory=True).result().get_counts()
    z_cleaned_counts_1 = {"z" + k[-1]: v for (k, v) in z_counts_1.items()}
    x_cleaned_counts_1 = {"x" + k[-1]: v for (k, v) in x_counts_1.items()}
    y_cleaned_counts_1 = {"y" + k[-1]: v for (k, v) in y_counts_1.items()}
    merged_counts_1 = z_cleaned_counts_1 | x_cleaned_counts_1 | y_cleaned_counts_1
    for missing in [x for x in ["x0", "x1", "y0", "y1", "z0", "z1"] if x not in merged_counts_1.keys()]:
        merged_counts_1[missing] = 0
    merged_counts_1 = {i: merged_counts_1[i] for i in ["x0", "x1", "y0", "y1", "z0", "z1"]}

    circuit_2.add_register(ClassicalRegister(1))
    c2z = measure_z(circuit_2.copy(), [qubit_register_2])
    c2x = measure_x(circuit_2.copy(), [qubit_register_2])
    c2y = measure_y(circuit_2.copy(), [qubit_register_2])
    z_counts_2 = execute(c2z, backend, shots=measurements, memory=True).result().get_counts()
    x_counts_2 = execute(c2x, backend, shots=measurements, memory=True).result().get_counts()
    y_counts_2 = execute(c2y, backend, shots=measurements, memory=True).result().get_counts()
    z_cleaned_counts_2 = {"z" + k[-1]: v for (k, v) in z_counts_2.items()}
    x_cleaned_counts_2 = {"x" + k[-1]: v for (k, v) in x_counts_2.items()}
    y_cleaned_counts_2 = {"y" + k[-1]: v for (k, v) in y_counts_2.items()}
    merged_counts_2 = z_cleaned_counts_2 | x_cleaned_counts_2 | y_cleaned_counts_2
    for missing in [x for x in ["x0", "x1", "y0", "y1", "z0", "z1"] if x not in merged_counts_2.keys()]:
        merged_counts_2[missing] = 0
    merged_counts_2 = {i: merged_counts_2[i] for i in ["x0", "x1", "y0", "y1", "z0", "z1"]}

    # calculate the chi-squared test statistic
    statistic, pvalue = sci.chisquare(f_obs=list(merged_counts_1.values()), f_exp=list(merged_counts_2.values()))

    return pvalue

def measure_y(circuit, qubit_indexes):
    cBitIndex = 0
    for index in qubit_indexes:
        circuit.sdg(index)
        circuit.h(index)
        circuit.measure(index, cBitIndex)
        cBitIndex += 1
    return circuit


def measure_z(circuit, qubit_indexes):
    cBitIndex = 0
    for index in qubit_indexes:
        circuit.measure(index, cBitIndex)
        cBitIndex += 1
    return circuit


def measure_x(circuit, qubit_indexes):
    cBitIndex = 0
    for index in qubit_indexes:
        circuit.h(index)
        circuit.measure(index, cBitIndex)
        cBitIndex += 1
    return circuit
