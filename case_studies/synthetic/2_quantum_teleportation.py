import random
import warnings

import numpy as np
from qiskit import QuantumCircuit, Aer
from qiskit.quantum_info import random_statevector

from case_studies.case_study_interface import CaseStudyInterface
from dd_regression.assertions.assertions import assertPhase
from dd_regression.assertions.assert_equal import assert_equal
from dd_regression.helper_functions import apply_edit_script, circuit_to_list, list_to_circuit, get_quantum_register
from dd_regression.result_classes import Passed, Failed
from dd_regression.diff_algorithm_r import Addition, Removal, diff, apply_diffs

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class QPESynthetic(CaseStudyInterface):
    def get_algorithm_name(self):
        return "Quantum Teleportation Synthetic"

    # passing circuit
    @staticmethod
    def quantum_teleportation():
        qc = QuantumCircuit(3)
        qc.x(0)  # d0 remove
        qc.x(0)  # d1 remove
        qc.h(1)
        qc.cx(1, 2)
        qc.cx(0, 1)  # d2 remove
        qc.h(0)
        qc.cx(1, 2)
        qc.cz(0, 2)
        return qc

    # failing circuit
    @staticmethod
    def quantum_teleportation_update():
        qc = QuantumCircuit(3)
        qc.h(1)
        qc.cx(1, 2)
        qc.cx(1, 0)  # d3 insert
        qc.h(0)
        qc.cx(1, 2)
        qc.cz(0, 2)
        return qc

    def expected_deltas_to_isolate(self):
        return []

    def passing_circuit(self):
        return self.quantum_teleportation()

    def failing_circuit(self):
        return self.quantum_teleportation_update()

    def regression_test(self, circuit_to_test):
        pass

    # generate circuit, and return if pass or fail
    def test_function(self, deltas, passing_circ, failing_circ):
        p_values = []

        # changed_circuit_list = apply_diffs(passing_circ, failing_circ, deltas)
        changed_circuit_list = apply_diffs(passing_circ, failing_circ, [])
        qlength, clength = get_quantum_register(changed_circuit_list)
        changed_circuit = list_to_circuit(changed_circuit_list)
        for j in range(1):
            # initialize to random state and append the applied delta modified circuit
            init_state = QuantumCircuit(qlength)
            init_vector = random_statevector(2)
            init_state.initialize(init_vector, 0)
            inputted_circuit_to_test = init_state + changed_circuit

            # create a new circuit with just state initialization to compare with
            qc = QuantumCircuit(1)
            qc.initialize(init_vector, 0)
            p_value = assert_equal(inputted_circuit_to_test, 2, qc, 0, measurements=5000)
            print(p_value)

            #need to store array of pvalues with inputs, as well as measurements
            #for each failure compare to original failure



    # # generate circuit, and return if pass or fail
    # def test_function(self, deltas, src_passing, src_failing, original_deltas):
    #     """"""
    #     p_values = []
    #
    #     passing_input_list = src_passing
    #     failing_input_list = src_failing
    #     # print(list_to_circuit(passing_input_list))
    #     changed_circuit_list = apply_edit_script(deltas, passing_input_list, failing_input_list, original_deltas)
    #     qlength, clength = get_quantum_register(changed_circuit_list)
    #     changed_circuit = list_to_circuit(changed_circuit_list)
    #     print("changed_circuit")
    #     print(changed_circuit)
    #
    #     for j in range(50):
    #         rotation = random.randrange(0, 8)
    #         x_circuit = QuantumCircuit(qlength)
    #         bin_amt = bin(rotation)[2:]
    #         for i in range(len(bin_amt)):
    #             if bin_amt[i] == '1':
    #                 x_circuit.x(len(bin_amt) - (i + 1))
    #
    #         inputted_circuit_to_test = x_circuit + changed_circuit
    #
    #         checks = []
    #         qubits = []
    #
    #         for i in range(inputted_circuit_to_test.num_qubits):
    #             checks.append(((360 / (2 ** (i + 1))) * rotation) % 360)
    #             qubits.append(i)
    #         pvals = assertPhase(backend, inputted_circuit_to_test, qubits, checks, 500)
    #         p_values += pvals
    #
    #     p_values = sorted(p_values)
    #
    #     for i in range(len(p_values)):
    #         if p_values[i] != np.NaN:
    #             if p_values[i] < 0.01 / (len(p_values) - i):
    #                 return Failed()
    #     return Passed()


if __name__ == "__main__":
    qpe = QPESynthetic()
    passing = qpe.passing_circuit()
    failing = qpe.failing_circuit()
    diff = diff(qpe.passing_circuit(), qpe.failing_circuit())
    print(diff)
    qpe.test_function(diff, passing, failing)


