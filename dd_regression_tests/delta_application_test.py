import unittest
import random
from hypothesis import given, settings
from hypothesis.strategies import composite, integers
from qiskit.circuit.random import random_circuit
from dd_regression.diff_algorithm import diff
from dd_regression.helper_functions import circuit_to_list, list_to_circuit, apply_edit_script, listminus, list_contains_list_in_same_order

@composite
def circuit(draw):
    num_qubits = draw(integers(min_value=1, max_value=10))
    depth = draw(integers(min_value=1, max_value=30))
    seed = draw(integers(min_value=0))
    return random_circuit(num_qubits=num_qubits, depth=depth, seed=seed)


def count_unhashable(list_obj):
    copy = list_obj.copy()
    ret = []
    while len(list_obj > 0):
        val = list_obj.pop(0)

class TestDeltaApplication(unittest.TestCase):
    # @given(circuit(), circuit())
    # @settings(deadline=10000)
    # def test_apply_edit_script_apply_all_deltas(self, circuit_1, circuit_2):
    #     c1 = circuit_to_list(circuit_1)
    #     c2 = circuit_to_list(circuit_2)
    #     diffs = diff(c1, c2)
    #     assert apply_edit_script(diffs, c1, c2, diffs) == c2
    #     assert apply_edit_script([], c1, c2, diffs) == c1

    # @given(circuit(), circuit())
    # @settings(deadline=10000)
    # def test_apply_edit_script_apply_subset_check_delete(self, circuit_1, circuit_2):
    #     if circuit_1 == circuit_2:
    #         circuit_2.x(0)
    #     c1 = circuit_to_list(circuit_1)
    #     c2 = circuit_to_list(circuit_2)
    #     diffs = diff(c1, c2)
    #     print("diffs")
    #     print(diffs)
    #     # sample = random.sample(diffs, len(diffs))
    #     sample = [random.choice(diffs)]
    #     print("sample")
    #     print(sample)
    #     applied_single_delta = apply_edit_script(sample, c1, c2, diffs)
    #     c1_copy = c1.copy()
    #     if sample[0]["operation"] == "delete":
    #         c1_copy.pop(sample[0]["position_old"])
    #         if not applied_single_delta == c1_copy:
    #             assert False

    @given(integers(min_value=1, max_value=3), integers(min_value=2, max_value=3), integers(min_value=0),
           integers(min_value=2, max_value=3), integers(min_value=0))
    @settings(deadline=10000)
    def test_apply_edit_script_apply_subset_check_amount_gates(self, num_qub, depth1, seed1, depth2, seed2):
        circuit_1 = random_circuit(num_qubits=num_qub, depth=depth1, seed=seed1)
        circuit_2 = random_circuit(num_qubits=num_qub, depth=depth2, seed=seed2)
        if circuit_1 == circuit_2:
            circuit_2.x(0)
        c1 = circuit_to_list(circuit_1)
        c2 = circuit_to_list(circuit_2)
        diffs = diff(c1, c2)
        sample = random.sample(diffs, len(diffs))
        applied_single_delta = apply_edit_script(sample, c1, c2, diffs)

        print(c1_gates)


if __name__ == '__main__':
    unittest.main()
