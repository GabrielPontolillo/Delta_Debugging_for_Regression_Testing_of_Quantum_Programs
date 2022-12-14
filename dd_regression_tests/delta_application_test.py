import unittest
import random
from hypothesis import given, settings
from hypothesis.strategies import composite, integers
from qiskit import QuantumCircuit
from qiskit.circuit.random import random_circuit
from dd_regression.diff_algorithm import diff
from dd_regression.helper_functions import circuit_to_list, list_to_circuit, apply_edit_script, listminus, list_contains_list_in_same_order

@composite
def circuit(draw):
    num_qubits = draw(integers(min_value=1, max_value=10))
    depth = draw(integers(min_value=1, max_value=30))
    seed = draw(integers(min_value=0))
    return random_circuit(num_qubits=num_qubits, depth=depth, seed=seed)


def simple_random_circuit(gates, register, seed):
    random.seed(seed)
    qc = QuantumCircuit(register)
    for i in range(gates):
        gate_r = random.randint(0, 4)
        qubit_r = random.randint(0, register-1)
        if gate_r == 0:
            qc.x(qubit_r)
        elif gate_r == 1:
            qc.y(qubit_r)
        elif gate_r == 2:
            qc.z(qubit_r)
        elif gate_r == 3:
            qc.h(qubit_r)
        elif gate_r == 4:
            qc.s(qubit_r)
    return qc


def count_unhashable(list_obj):
    copy = list_obj.copy()
    element = []
    count = []
    while len(copy) > 0:
        val = copy.pop(0)
        if val not in element:
            element.append(val)
            count.append(1)
        else:
            idx = element.index(val)
            count[idx] = count[idx] + 1
    return element, count


def count_unhashable_deltas(delta_sample_list, c1, c2):
    elem = []
    count = []
    for delta in delta_sample_list:
        if delta["operation"] == "delete":
            instruction = c1[delta["position_old"]]
            if instruction not in elem:
                elem.append(instruction)
                count.append(-1)
            else:
                idx = elem.index(instruction)
                count[idx] = count[idx] - 1
        else:
            instruction = c2[delta["position_new"]]
            if instruction not in elem:
                elem.append(instruction)
                count.append(1)
            else:
                idx = elem.index(instruction)
                count[idx] = count[idx] + 1
    return zip(elem, count)

class TestDeltaApplication(unittest.TestCase):
    # @given(circuit(), circuit())
    # @settings(deadline=10000)
    # def test_apply_edit_script_apply_all_deltas(self, circuit_1, circuit_2):
    #     c1 = circuit_to_list(circuit_1)
    #     c2 = circuit_to_list(circuit_2)
    #     diffs = diff(c1, c2)
    #     assert apply_edit_script(diffs, c1, c2, diffs) == c2
    #     assert apply_edit_script([], c1, c2, diffs) == c1

    # @given(integers(min_value=1, max_value=3), integers(min_value=2, max_value=10), integers(min_value=0),
    #        integers(min_value=2, max_value=10), integers(min_value=0))
    # @settings(deadline=10000)
    # def test_apply_edit_script_apply_subset_check_amount_gates(self, num_qub, depth1, seed1, depth2, seed2):
    #     circuit_1 = random_circuit(num_qubits=num_qub, depth=depth1, seed=seed1)
    #     circuit_2 = random_circuit(num_qubits=num_qub, depth=depth2, seed=seed2)
    #     if circuit_1 == circuit_2:
    #         circuit_2.x(0)
    #     c1 = circuit_to_list(circuit_1)
    #     c2 = circuit_to_list(circuit_2)
    #     diffs = diff(c1, c2)
    #     sample = random.sample(diffs, len(diffs))
    #     applied_sample_delta = apply_edit_script(sample, c1, c2, diffs)
    #     c1_inst, count = count_unhashable(c1)
    #     applied_inst, count_applied = count_unhashable(applied_sample_delta)
    #     modifier = count_unhashable_deltas(sample, c1, c2)
    #     for instruction, value in modifier:
    #         try:
    #             idx_c1 = c1_inst.index(instruction)
    #             c1_count = count[idx_c1]
    #         except ValueError:
    #             c1_count = 0
    #         try:
    #             idx_applied = applied_inst.index(instruction)
    #             applied_count = count_applied[idx_applied]
    #         except ValueError:
    #             applied_count = 0
    #         assert applied_count - c1_count == value

    @given(integers(min_value=1, max_value=1), integers(min_value=1, max_value=7), integers(min_value=0),
           integers(min_value=1, max_value=7), integers(min_value=0))
    @settings(deadline=10000)
    def test_apply_edit_script_apply_subset_check_position_gates(self, num_qub, depth1, seed1, depth2, seed2):
        # circuit_1 = random_circuit(num_qubits=num_qub, depth=depth1, seed=seed1)
        # circuit_2 = random_circuit(num_qubits=num_qub, depth=depth2, seed=seed2)
        circuit_1 = simple_random_circuit(depth1, num_qub, seed1)
        circuit_2 = simple_random_circuit(depth2, num_qub, seed2)
        if circuit_1 == circuit_2:
            circuit_2.x(0)
        print(circuit_1)
        print(circuit_2)
        c1 = circuit_to_list(circuit_1)
        c2 = circuit_to_list(circuit_2)
        diffs = diff(c1, c2)
        [print(s) for s in diffs]
        # Create a list of random indices
        indices = random.sample(range(len(diffs)), random.randint(1, len(diffs)))

        # Use the indices to select the elements from the original list
        # and keep the order of the indices
        sample = [diffs[i] for i in sorted(indices)]

        applied_sample_delta = apply_edit_script(sample, c1, c2, diffs)

        # List of keys to keep in the new list
        keys_to_keep = ['operation', 'position_old', 'position_new']

        # Create a new list of dictionaries with only the specified keys
        sample_copy = [{k: d.get(k) for k in keys_to_keep if d.get(k) is not None} for d in sample]

        print("sample copy")
        print(sample_copy)

        print(list_to_circuit(applied_sample_delta))
        [print(s) for s in diffs]
        print("---------------")
        [print(s) for s in sample]
        print("@---@")
        for delta in sample:
            if delta["operation"] == "insert":
                delta.pop("offset")
                print(delta)
                pos_old = delta["position_old"]
                print("before this gate")
                if len(c1) == pos_old:
                    print("we need to place it at end")
                else:
                    print(c1[delta["position_old"]])
                print("what we are inserting")
                print(c2[delta["position_new"]])
                assert c2[delta["position_new"]] in applied_sample_delta
                # make sure we are not deleting that gate we are checking for
                if {"operation": "delete", "position_old": pos_old} not in sample_copy:
                    # if not placing at end
                    # if check that there exists one version of the gate s.t. after it, we have the replaced gate
                    if len(c1) != pos_old:
                        found = False
                        # check each instance of gate we inserted, if we do not find the gate that is supposed to be after (if it was not deleted)
                        # assert false
                        for idx, gate in enumerate(applied_sample_delta):
                            if gate == c2[delta["position_new"]]:
                                print("check")
                                print(applied_sample_delta[idx+1:])
                                print(applied_sample_delta[idx:])
                                if c1[delta["position_old"]] in applied_sample_delta[idx+1:]:
                                    found = True
                                    break
                        print("this ran?")
                        assert found
                        # after_app = applied_sample_delta[pos_old-1:]
                        # print(applied_sample_delta)
                        # print(after_app)
                        # assert c1[delta["position_old"]] in after_app


if __name__ == '__main__':
    unittest.main()
