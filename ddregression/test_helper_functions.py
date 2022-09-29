import unittest
from entangle_qiskit_example import qiskit_entangle, qiskit_entangle_circ, qiskit_entangle_circ_chaff_and_i
from entangle_qiskit_example_after_patch import qiskit_entangle_patched, qiskit_entangle_patched_circ
from test_regression import ret_passing, ret_failing
from helper_functions import apply_edit_script, circuit_to_list, list_to_circuit
from diff_algorithm import diff, print_edit_sequence
from qiskit import Aer, QuantumCircuit

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)


class TestHelpers(unittest.TestCase):
    def test_chaff_and_i(self):
        failing_circuit = qiskit_entangle_circ_chaff_and_i()
        failing_input_list = circuit_to_list(failing_circuit)

        passing_circuit = qiskit_entangle_patched_circ()
        passing_input_list = circuit_to_list(passing_circuit)

        print(passing_circuit)
        print(failing_circuit)

        orig_deltas = diff(passing_input_list, failing_input_list)

        changes = [orig_deltas[4], orig_deltas[7], orig_deltas[8]]
        print(changes)

        changed_circuit_list = apply_edit_script(changes, passing_input_list,
                                                 failing_input_list, orig_deltas)

        expected_result = [passing_input_list[0], passing_input_list[1], passing_input_list[2], passing_input_list[3],
                           passing_input_list[4], failing_input_list[7], failing_input_list[8], failing_input_list[9]]

        assert(changed_circuit_list == expected_result)

    def test_remove_deletion(self):
        passing_circuit = QuantumCircuit(2)
        passing_circuit.y(0)
        passing_circuit.i(0)
        passing_circuit.x(1)
        passing_input_list = circuit_to_list(passing_circuit)

        failing_circuit = QuantumCircuit(2)
        failing_circuit.x(0)
        failing_circuit.x(1)
        failing_input_list = circuit_to_list(failing_circuit)

        orig_deltas = diff(passing_input_list, failing_input_list)
        print(orig_deltas)

        changes = [orig_deltas[1], orig_deltas[2]]
        print(changes)

        changed_circuit_list = apply_edit_script(changes, passing_input_list,
                                                 failing_input_list, orig_deltas)

        expected_result = [passing_input_list[0], failing_input_list[0], failing_input_list[1]]

        assert (changed_circuit_list == expected_result)

    def test_remove_insertion(self):
        passing_circuit = QuantumCircuit(2)
        passing_circuit.x(0)
        passing_circuit.x(1)
        passing_circuit.x(1)
        passing_input_list = circuit_to_list(passing_circuit)

        failing_circuit = QuantumCircuit(2)
        failing_circuit.i(0)
        failing_circuit.i(0)
        failing_circuit.x(0)
        failing_circuit.x(1)
        failing_circuit.y(1)
        failing_input_list = circuit_to_list(failing_circuit)

        orig_deltas = diff(passing_input_list, failing_input_list)
        print(orig_deltas)

        changes = [orig_deltas[1], orig_deltas[2], orig_deltas[3]]
        print(changes)

        changed_circuit_list = apply_edit_script(changes, passing_input_list,
                                                 failing_input_list, orig_deltas)

        expected_result = [failing_input_list[1], failing_input_list[2], failing_input_list[3], failing_input_list[4]]

        assert (changed_circuit_list == expected_result)

    def test_remove_2_insertion(self):
        passing_circuit = QuantumCircuit(2)
        passing_circuit.x(0)
        passing_circuit.x(1)
        passing_circuit.x(1)
        passing_input_list = circuit_to_list(passing_circuit)

        failing_circuit = QuantumCircuit(2)
        failing_circuit.i(0)
        failing_circuit.i(0)
        failing_circuit.x(0)
        failing_circuit.x(1)
        failing_circuit.y(1)
        failing_input_list = circuit_to_list(failing_circuit)

        orig_deltas = diff(passing_input_list, failing_input_list)
        print(orig_deltas)

        changes = [orig_deltas[2], orig_deltas[3]]
        print(changes)

        changed_circuit_list = apply_edit_script(changes, passing_input_list,
                                                 failing_input_list, orig_deltas)

        expected_result = [failing_input_list[2], failing_input_list[3], failing_input_list[4]]

        assert (changed_circuit_list == expected_result)

    def test_qft(self):
        length = 3
        rotation = 7

        passing_circuit = ret_passing(length, rotation)
        # print(passing_circuit)
        passing_input_list = circuit_to_list(passing_circuit)

        failing_circuit = ret_failing(length, rotation)
        # print(failing_circuit)
        failing_input_list = circuit_to_list(failing_circuit)

        orig_deltas = diff(passing_input_list, failing_input_list)
        print("passing\n")
        for val in passing_input_list:
            print(val)

        print("failing\n")
        for val in failing_input_list:
            print(val)

        print_edit_sequence(orig_deltas, passing_input_list, failing_input_list)

        changes = orig_deltas[8:]
        # print(changes)

        print_edit_sequence(changes, passing_input_list, failing_input_list)

        changed_circuit_list = apply_edit_script(changes, passing_input_list,
                                                 failing_input_list, orig_deltas)

        # print(changed_circuit_list)
        # for s in changed_circuit_list:
        #     print(s)
        #
        expected_result = [passing_input_list[0], passing_input_list[1], passing_input_list[2], failing_input_list[11],
                           failing_input_list[12], failing_input_list[13], failing_input_list[14], failing_input_list[15],
                           failing_input_list[16], failing_input_list[17]]

        assert (changed_circuit_list == expected_result)


if __name__ == '__main__':
    unittest.main()
