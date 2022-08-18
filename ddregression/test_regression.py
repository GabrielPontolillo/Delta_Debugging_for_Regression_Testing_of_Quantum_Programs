from result_classes import Passed, Failed, Inconclusive
from diff_algorithm import diff
from dd import dd, split, listunion, listminus
from helper_functions import apply_edit_script, circuit_to_list, list_to_circuit
from assertions import assertPhase

import pandas as pd
import inspect
import scipy.stats as sci
import math
import copy
import qiskit
import random
import numpy as np
import itertools
from typing import List
from qiskit import QuantumCircuit, Aer, execute
from qiskit.circuit import Gate, ClassicalRegister
from qiskit.circuit.library import QFT
import qiskit.circuit.random as ra
from qiskit.quantum_info.states import Statevector

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

pi = np.pi
backend = Aer.get_backend('aer_simulator')


def QFT_basic():
    qft_circuit = QuantumCircuit(3)
    for i in range(3):
        qft_circuit.h(2 - i)
        phase_ctr = 2 - i
        for j in range(2 - i):
            qft_circuit.cp(pi / 2 ** phase_ctr, j, 2 - i)
            phase_ctr -= 1
    return qft_circuit


def QFT_variable_length(num):
    qft_circuit = QuantumCircuit(num)
    for i in range(num):
        qft_circuit.h((num - 1) - i)
        phase_ctr = (num) - i
        for j in range((num - 1) - i):
            qft_circuit.cp(pi / 2 ** phase_ctr, j, (num - 1) - i)
            phase_ctr -= 1
    return qft_circuit


def QFT_variable_length_correct(num):
    qft_circuit = QuantumCircuit(num)
    for i in range(num):
        qft_circuit.h((num - 1) - i)
        phase_ctr = (num - 1) - i
        for j in range((num - 1) - i):
            qft_circuit.cp(pi / 2 ** phase_ctr, j, (num - 1) - i)
            phase_ctr -= 1
    return qft_circuit


def test_qft(qft_circuit, rotation_amount):
    x_circuit = QuantumCircuit(qft_circuit.num_qubits)
    bin_amt = bin(rotation_amount)[2:]
    print(bin_amt)
    for i in range(len(bin_amt)):
        if bin_amt[i] == '1':
            x_circuit.x(len(bin_amt) - (i + 1))

    qft_circuit = x_circuit + qft_circuit

    print(qft_circuit)

    checks = []
    qubits = []

    res = 0
    for i in range(qft_circuit.num_qubits):
        checks.append(((360 / (2 ** (i + 1))) * rotation_amount) % 360)
        qubits.append(i)
    print(checks)
    print(qubits)
    pvals = assertPhase(backend, qft_circuit, qubits, checks, 100000)
    print(pvals)
    for res in pvals:
        if res != np.NaN and res < 0.01:
            assert False
    assert True


# def test(changes: List[any]):
#     """"""
#     rotation = 7
#     length = 3
#     passing_input_list = circuit_to_list(ret_passing(length, rotation))
#     failing_input_list = circuit_to_list(ret_failing(length, rotation))
#     changed_circuit_list = apply_edit_script(changes, passing_input_list, failing_input_list)
#     changed_circuit = list_to_circuit(changed_circuit_list, ret_passing(length, rotation).num_qubits)
#
#     print(changed_circuit)
#
#     checks = []
#     qubits = []
#
#     res = 0
#     for i in range(changed_circuit.num_qubits):
#         checks.append(((360 / (2 ** (i + 1))) * rotation) % 360)
#         qubits.append(i)
#     print(checks)
#     print(qubits)
#     pvals = assertPhase(backend, changed_circuit, qubits, checks, 100000)
#     #     print(estimatePhase(backend, qft_circuit, qubits, 100000))
#     print(pvals)
#     for res in pvals:
#         if res != np.NaN and res < 0.01:
#             return Failed()
#     return Passed()

def test(changes: List[any]):
    """"""
    rotation = 7
    length = 3
    #passing_input_list = circuit_to_list(ret_passing(length, rotation))
    #failing_input_list = circuit_to_list(ret_failing(length, rotation))
    modified_function = apply_edit_script(changes, ret_passing(length, rotation), ret_failing(length, rotation))
    print(modified_function)
    changed_circuit = list_to_circuit(changed_circuit_list, ret_passing(length, rotation).num_qubits)

    print(changed_circuit)

    checks = []
    qubits = []

    res = 0
    for i in range(changed_circuit.num_qubits):
        checks.append(((360 / (2 ** (i + 1))) * rotation) % 360)
        qubits.append(i)
    print(checks)
    print(qubits)
    pvals = assertPhase(backend, changed_circuit, qubits, checks, 100000)
    #     print(estimatePhase(backend, qft_circuit, qubits, 100000))
    print(pvals)
    for res in pvals:
        if res != np.NaN and res < 0.01:
            return Failed()
    return Passed()


# def ret_passing(length, rotation):
#     x_circuit = QuantumCircuit(length)
#     bin_amt = bin(rotation)[2:]
#     print(bin_amt)
#     for i in range(len(bin_amt)):
#         if bin_amt[i] == '1':
#             x_circuit.x(len(bin_amt) - (i + 1))
#     passing = QFT_basic()
#     passing = x_circuit + passing
#     return passing

def ret_passing(length, rotation):
    x_circuit = QuantumCircuit(length)
    bin_amt = bin(rotation)[2:]
    print(bin_amt)
    for i in range(len(bin_amt)):
        if bin_amt[i] == '1':
            x_circuit.x(len(bin_amt) - (i + 1))
    qft_circuit = QuantumCircuit(length)
    for i in range(length):
        qft_circuit.h((length - 1) - i)
        phase_ctr = (length - 1) - i
        for j in range((length - 1) - i):
            qft_circuit.cp(pi / 2 ** phase_ctr, j, (length - 1) - i)
            phase_ctr -= 1
    passing = qft_circuit
    passing = x_circuit + passing
    return passing


# def ret_failing(length, rotation):
#     x_circuit = QuantumCircuit(length)
#     bin_amt = bin(rotation)[2:]
#     print(bin_amt)
#     for i in range(len(bin_amt)):
#         if bin_amt[i] == '1':
#             x_circuit.x(len(bin_amt) - (i + 1))
#     failing = QFT_variable_length(length)
#     failing = x_circuit + failing
#     return failing


def ret_failing(length, rotation):
    x_circuit = QuantumCircuit(length)
    bin_amt = bin(rotation)[2:]
    print(bin_amt)
    for i in range(len(bin_amt)):
        if bin_amt[i] == '1':
            x_circuit.x(len(bin_amt) - (i + 1))
    qft_circuit = QuantumCircuit(length)
    for i in range(length):
        qft_circuit.h((length - 1) - i)
        phase_ctr = (length) - i
        for j in range((length - 1) - i):
            qft_circuit.cp(pi / 2 ** phase_ctr, j, (num - 1) - i)
            phase_ctr -= 1
    failing = qft_circuit
    failing = x_circuit + failing
    return failing


if __name__ == "__main__":
    # rotation = 7
    # length = 3
    #
    # failing = ret_failing(length, rotation)
    #
    # failing_input_list = circuit_to_list(failing)
    #
    # passing = ret_passing(length, rotation)
    #
    # passing_input_list = circuit_to_list(passing)
    #
    # fail_deltas = diff(passing_input_list, failing_input_list)
    # pass_deltas = []
    #
    # print(fail_deltas)
    # test(fail_deltas)
    #
    # passdiff, faildiff = dd(pass_deltas, fail_deltas, test)
    # print(passdiff)
    # print(faildiff)
    # print(test(passdiff))
    # print(test(faildiff))

    srcfail = inspect.getsource(ret_passing)
    srcpass = inspect.getsource(ret_failing)
    print(srcfail)
    fail_deltas = diff(srcpass, srcfail)
    pass_deltas = []
    #
    # print(fail_deltas)

    test(fail_deltas)
