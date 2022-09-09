from result_classes import Passed, Failed, Inconclusive
from diff_algorithm import diff, print_edit_sequence
from dd import dd, split, listunion, listminus
from helper_functions import apply_edit_script, circuit_to_list, list_to_circuit
from assertions import assertPhase

from entangle_qiskit_example import qiskit_entangle, qiskit_entangle_circ
from entangle_qiskit_example_after_patch import qiskit_entangle_patched, qiskit_entangle_patched_circ

import inspect
import numpy as np
from typing import List
from qiskit import QuantumCircuit, Aer, execute
from qiskit.quantum_info import partial_trace, Statevector
from qiskit.visualization import plot_state_city


import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

pi = np.pi
backend = Aer.get_backend('aer_simulator')


def select_qubit_state(circuit, num):
    """https://quantumcomputing.stackexchange.com/questions/15110/get-state-vector-of-a-single-qubit-in-a-circuit-in-qiskit"""
    """Get the statevector for the first qubit, discarding the rest."""
    # get the full statevector of all qubits
    full_statevector = Statevector(circuit)

    # get the density matrix for the first qubit by taking the partial trace
    partial_density_matrix = partial_trace(full_statevector, [num])

    # extract the statevector out of the density matrix
    partial_statevector = np.diagonal(partial_density_matrix)

    return partial_statevector


if __name__ == "__main__":
    print(qiskit_entangle_circ())
    print(qiskit_entangle_patched_circ())

    qc1 = QuantumCircuit(2)
    qc1.x(1)
    qc1.h(1)
    qc1.cx(1, 0)
    qc1.cx(0, 1)
    qc1.h(0)
    sv_qc1 = Statevector.from_instruction(qc1)
    print(qc1)
    print(sv_qc1)
    print(select_qubit_state(sv_qc1, 1))
    print(select_qubit_state(sv_qc1, 0))

    qc2 = QuantumCircuit(2)
    qc2.x(1)
    qc2.h(1)
    qc2.cx(1, 0)
    qc2.cx(1, 0)
    qc2.h(1)
    sv_qc2 = Statevector.from_instruction(qc2)
    print(qc2)
    print(sv_qc2)
    print(select_qubit_state(qc2, 1))
    print(select_qubit_state(qc2, 0))

    #
    # sv = Statevector.from_label('00')
    # sv.evolve(qc)
    # plot_state_city(sv)

