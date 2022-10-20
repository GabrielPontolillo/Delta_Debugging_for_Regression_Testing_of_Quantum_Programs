from result_classes import Passed, Failed, Inconclusive
from diff_algorithm import diff, print_edit_sequence
from dd import dd, split, listunion, listminus
from helper_functions import apply_edit_script, circuit_to_list, list_to_circuit, get_quantum_register
from assertions import assertPhase
from test_entangled_qiskit import dd_repeat, further_narrowing

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
        phase_ctr = num - i
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
    pvals = assertPhase(backend, qft_circuit, qubits, checks, 100000)
    print(pvals)
    for res in pvals:
        if res != np.NaN and res < 0.05/len(pvals):
            assert False
    assert True


def test_circuit(changes: List[any], src_pass, src_fail, orig_deltas):
    """"""
    p_values = []

    passing_input_list = src_pass
    failing_input_list = src_fail
    changed_circuit_list = apply_edit_script(changes, passing_input_list, failing_input_list, orig_deltas)
    qlength, clength = get_quantum_register(changed_circuit_list)
    changed_circuit = list_to_circuit(changed_circuit_list)

    for j in range(100):
        rotation = random.randrange(0, 8)
        x_circuit = QuantumCircuit(qlength)
        bin_amt = bin(rotation)[2:]
        for i in range(len(bin_amt)):
            if bin_amt[i] == '1':
                x_circuit.x(len(bin_amt) - (i + 1))

        inputted_circuit_to_test = x_circuit + changed_circuit

        checks = []
        qubits = []

        for i in range(inputted_circuit_to_test.num_qubits):
            checks.append(((360 / (2 ** (i + 1))) * rotation) % 360)
            qubits.append(i)
        pvals = assertPhase(backend, inputted_circuit_to_test, qubits, checks, 1000)
        p_values += pvals

    p_values = sorted(p_values)

    for i in range(len(p_values)):
        if p_values[i] != np.NaN:
            if p_values[i] < 0.01/(len(p_values)-i):
                return Failed()
    return Passed()


# def test_circuit(changes: List[any], src_pass, src_fail, orig_deltas):
#     """"""
#     passing_input_list = src_pass
#     failing_input_list = src_fail
#     changed_circuit_list = apply_edit_script(changes, passing_input_list, failing_input_list,  orig_deltas)
#     changed_circuit = list_to_circuit(changed_circuit_list)
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
#     pvals = assertPhase(backend, changed_circuit, qubits, checks, 10000)
#     #     print(estimatePhase(backend, qft_circuit, qubits, 100000))
#     print(pvals)
#     for res in pvals:
#         if res != np.NaN and res < 0.005:
#             return Failed()
#     return Passed()


def regression_test_circuit(circuit_to_test):
    """"""
    p_values = []
    qlength, clength = get_quantum_register(circuit_to_list(circuit_to_test))
    for j in range(100):
        rotation = random.randrange(0, 8)
        x_circuit = QuantumCircuit(qlength)
        bin_amt = bin(rotation)[2:]
        for i in range(len(bin_amt)):
            if bin_amt[i] == '1':
                x_circuit.x(len(bin_amt) - (i + 1))

        inputted_circuit_to_test = x_circuit + circuit_to_test

        checks = []
        qubits = []

        for i in range(inputted_circuit_to_test.num_qubits):
            checks.append(((360 / (2 ** (i + 1))) * rotation) % 360)
            qubits.append(i)

        pvals = assertPhase(backend, inputted_circuit_to_test, qubits, checks, 1000)
        p_values += pvals

    p_values = sorted(p_values)
    for i in range(len(p_values)):
        if p_values[i] != np.NaN:
            if p_values[i] < 0.05/(len(p_values)-i):
                assert False
    assert True


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

def ret_passing(length):
    qft_circuit = QuantumCircuit(length)
    for i in range(length):
        qft_circuit.h((length - 1) - i)
        phase_ctr = (length - 1) - i
        for j in range((length - 1) - i):
            qft_circuit.cp(pi / 2 ** phase_ctr, j, (length - 1) - i)
            phase_ctr -= 1
    return qft_circuit


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


def ret_failing(length):
    qft_circuit = QuantumCircuit(length)
    qft_circuit.x(0)
    qft_circuit.x(0)
    qft_circuit.i(1)
    qft_circuit.x(0)
    qft_circuit.x(0)
    qft_circuit.x(1)
    qft_circuit.x(1)
    qft_circuit.x(1)
    qft_circuit.x(1)
    for i in range(length):
        qft_circuit.h((length - 1) - i)
        phase_ctr = length - i
        for j in range((length - 1) - i):
            qft_circuit.cp(pi / 2 ** phase_ctr, j, (length - 1) - i)
            phase_ctr -= 1
    return qft_circuit


if __name__ == "__main__":
    #test_circ()
    rotation = 0
    # rotation = 7
    length = 3
    deltas, orig_fail_deltas = dd_repeat(ret_passing(length), ret_failing(length), test_circuit)
    print("the deltas")
    print(deltas)
    # refined_deltas = further_narrowing(ret_passing(length), ret_failing(length),
    #                                    deltas, orig_fail_deltas, test_circuit)
    # print_edit_sequence(refined_deltas, circuit_to_list(ret_passing(length)),
    #                     circuit_to_list(ret_failing(length)))

    # print(QFT_basic())
    # regression_test_circuit(QFT_basic())
