import random
import warnings

import numpy as np
from qiskit import QuantumCircuit, Aer

from case_studies.case_study_interface import CaseStudyInterface
from dd_regression.assertions import assertPhase
from dd_regression.helper_functions import apply_edit_script, circuit_to_list, list_to_circuit, get_quantum_register, \
    add_random_chaff
from dd_regression.result_classes import Passed, Failed

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class QFTSynthetic(CaseStudyInterface):
    # failing circuit without parameter input for length
    # fixed length of 3
    @staticmethod
    def qft_basic():
        qft_circuit = QuantumCircuit(3)
        for i in range(3):
            qft_circuit.h(2 - i)
            phase_ctr = 2 - i
            for j in range(2 - i):
                qft_circuit.cp(np.pi / 2 ** phase_ctr, j, 2 - i)
                phase_ctr -= 1
        return qft_circuit

    @staticmethod
    def qft_update(length):
        qft_circuit = QuantumCircuit(length)
        # qft_circuit.x(0)
        # qft_circuit.x(0)
        # qft_circuit.i(1)
        # qft_circuit.x(0)
        # qft_circuit.x(0)
        # qft_circuit.x(1)
        # qft_circuit.x(1)
        # qft_circuit.x(1)
        # qft_circuit.x(1)
        for i in range(length):
            qft_circuit.h((length - 1) - i)
            phase_ctr = length - i
            for j in range((length - 1) - i):
                qft_circuit.cp(np.pi / 2 ** phase_ctr, j, (length - 1) - i)
                phase_ctr -= 1
        return qft_circuit

    def expected_deltas_to_isolate(self):
        return [{'operation': 'delete', 'position_old': 1},
                {'operation': 'insert', 'position_old': 2, 'position_new': 1},
                {'operation': 'delete', 'position_old': 2},
                {'operation': 'insert', 'position_old': 3, 'position_new': 2},
                {'operation': 'insert', 'position_old': 4, 'position_new': 4},
                {'operation': 'delete', 'position_old': 4}]

    def passing_circuit(self):
        return self.qft_basic()

    def failing_circuit(self):
        return self.qft_update(3)

    def regression_test(self, circuit_to_test):
        p_values = []
        q_length, c_length = get_quantum_register(circuit_to_list(circuit_to_test))
        for j in range(50):
            rotation = random.randrange(0, 8)
            x_circuit = QuantumCircuit(q_length)
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
                if p_values[i] < 0.01 / (len(p_values) - i):
                    assert False
        assert True

    def test_function(self, deltas, src_passing, src_failing, original_deltas):
        """"""
        p_values = []

        passing_input_list = src_passing
        failing_input_list = src_failing
        print(list_to_circuit(passing_input_list))
        changed_circuit_list = apply_edit_script(deltas, passing_input_list, failing_input_list, original_deltas)
        qlength, clength = get_quantum_register(changed_circuit_list)
        changed_circuit = list_to_circuit(changed_circuit_list)
        print("changed_circuit")
        print(changed_circuit)

        # for j in range(50):
        #     rotation = random.randrange(0, 8)
        #     x_circuit = QuantumCircuit(qlength)
        #     bin_amt = bin(rotation)[2:]
        #     for i in range(len(bin_amt)):
        #         if bin_amt[i] == '1':
        #             x_circuit.x(len(bin_amt) - (i + 1))
        #
        #     inputted_circuit_to_test = x_circuit + changed_circuit
        #
        #     checks = []
        #     qubits = []
        #
        #     for i in range(inputted_circuit_to_test.num_qubits):
        #         checks.append(((360 / (2 ** (i + 1))) * rotation) % 360)
        #         qubits.append(i)
        #     pvals = assertPhase(backend, inputted_circuit_to_test, qubits, checks, 500)
        #     p_values += pvals

        for j in range(8):
            rotation = j
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
            pvals = assertPhase(backend, inputted_circuit_to_test, qubits, checks, 10000)
            p_values += pvals

        p_values = sorted(p_values)

        for i in range(len(p_values)):
            if p_values[i] != np.NaN:
                if p_values[i] < 0.01 / (len(p_values) - i):
                    return Failed()
        return Passed()


if __name__ == "__main__":
    qft = QFTSynthetic()
    qft.analyse_results()

