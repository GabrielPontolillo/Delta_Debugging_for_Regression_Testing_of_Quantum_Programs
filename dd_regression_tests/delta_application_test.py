import unittest
import random
import time
from hypothesis import given, settings, assume
from hypothesis.strategies import composite, integers, text, lists, characters
from qiskit import QuantumCircuit
from qiskit.circuit.random import random_circuit
from dd_regression.diff_algorithm_r import diff, apply_diffs, Addition, Removal
from dd_regression.helper_functions import circuit_to_list, list_to_circuit, listminus, list_contains_list_in_same_order


@composite
def circuit(draw):
    num_qubits = draw(integers(min_value=1, max_value=6))
    depth = draw(integers(min_value=1, max_value=20))
    # seed = draw(integers(min_value=0))
    return random_circuit(num_qubits=num_qubits, depth=depth)


class TestDeltaApplication(unittest.TestCase):
    @given(s1=lists(characters()), s2=lists(characters()))
    @settings(deadline=30000)
    def test_apply_edit_script_sample_ordering_check_before_subset(self, s1, s2):
        assume(s1 != s2)
        print(f" - new test - ")
        # print(f"s1 {s1}")
        # print(f"s2 {s2}")
        diffs = diff(s1, s2)
        # print(f"diffs {diffs}")
        # Create a list of random indices
        sample = ordered_sample(diffs)
        applied = apply_diffs(s1, s2, sample)
        print(f"applied {applied}")
        s1c = [("a"+str(i), x) for i, x in enumerate(s1)]
        s2c = [("b"+str(i), x) for i, x in enumerate(s2)]
        applied_2 = apply_diffs(s1c, s2c, sample)
        applied_base = apply_diffs(s1c, s2c, diffs)
        # need to match
        print(f"s1c {s1c}")
        print(f"s2c {s2c}")
        print(f"sample {sample}")
        print(f"applied 2 {applied_2}")
        print(f"applied base {applied_base}")
        removal_idx = [x.location_index for x in sample if isinstance(x, Removal)]
        print(removal_idx)
        for i, elem in enumerate(applied_2):
            for delta in sample:
                if isinstance(delta, Addition):
                    if s2c[delta.add_gate_index] == elem:
                        print(delta.location_index)
                        print(s1c[:delta.location_index])
                        # get all elements from list 1 that were not removed by deltas,
                        # check that they are present in output of applied list before addition location in orig circuit
                        before_non_removed = [x for idx, x in enumerate(s1c[:delta.location_index]) if idx not in removal_idx]
                        print(f"gates we need to see {before_non_removed}")
                        print(f"before current addition {applied_2[:i]}")
                        assert all(x in applied_2[:i] for x in before_non_removed)
                        #look at all gates before this index on s1, if not removed they should be present in output


    @given(s1=lists(characters()), s2=lists(characters()))
    @settings(deadline=30000)
    def test_apply_edit_script_sample_ordering_separate_lists(self, s1, s2):
        assume(s1 != s2)
        print(f" - new test - ")
        print(f"s1 {s1}")
        print(f"s2 {s2}")
        diffs = diff(s1, s2)
        print(f"diffs {diffs}")
        # Create a list of random indices
        sample = ordered_sample(diffs)
        applied = apply_diffs(s1, s2, sample)
        print(f"applied {applied}")
        s1c = [("a"+str(i), x) for i, x in enumerate(s1)]
        s2c = [("b"+str(i), x) for i, x in enumerate(s2)]
        applied_2 = apply_diffs(s1c, s2c, sample)
        a_idx, b_idx = -1, -1
        print(f"applied_2 {applied_2}")
        for elem in applied_2:
            if elem[0][0] == 'a':
                if int(elem[0][1:]) > a_idx:
                    a_idx = int(elem[0][1:])
                else:
                    assert False
            elif elem[0][0] == 'b':
                if int(elem[0][1:]) > b_idx:
                    b_idx = int(elem[0][1:])
                else:
                    assert False
            else:
                assert False


    @given(s1=lists(characters()), s2=lists(characters()))
    @settings(deadline=30000)
    def test_apply_edit_script_sample(self, s1, s2):
        assume(s1 != s2)
        print(f" - new test - ")
        print(f"s1 {s1}")
        print(f"s2 {s2}")
        diffs = diff(s1, s2)
        print(f"diffs {diffs}")
        # Create a list of random indices
        sample = ordered_sample(diffs)
        applied = apply_diffs(s1, s2, sample)
        print(f"applied {applied}")
        occurences_s1 = count_occurrences(s1)
        occurences_applied = count_occurrences(applied)
        modifier_deltas = deltas_to_modifier(sample, s1, s2)
        print(f"occurences s1 {occurences_s1}")
        print(f"modifier deltas {modifier_deltas}")
        print(occurences_s1.keys() & modifier_deltas.keys())
        # add delta modifier to s1 occurences
        result = {key: occurences_s1.get(key, 0) + modifier_deltas.get(key, 0) for key in occurences_s1.keys() | modifier_deltas.keys()}
        print(f"result {result}")
        result_cleaned = {key: value for key, value in result.items() if value != 0}
        print(f"result cleaned {result_cleaned}")
        print(f"occurences applied {occurences_applied}")
        assert result_cleaned == occurences_applied


    @given(circuit(), circuit())
    @settings(deadline=30000)
    def test_apply_edit_script_apply_all_deltas(self, circuit_1, circuit_2):
        c1 = circuit_to_list(circuit_1)
        c2 = circuit_to_list(circuit_2)
        diffs = diff(c1, c2)
        print(list_to_circuit(c1))
        print(list_to_circuit(c2))
        print(diffs)
        assert apply_diffs(c1, c2, diffs) == c2
        assert apply_diffs(c1, c2, []) == c1


    @given(lists(characters()), lists(characters()))
    @settings(deadline=30000)
    def test_apply_edit_script_apply_all_deltas_string(self, s1, s2):
        diffs = diff(s1, s2)
        assert apply_diffs(s1, s2, diffs) == s2
        assert apply_diffs(s1, s2, []) == s1



def simple_random_circuit(gates, register, seed):
    random.seed(seed)
    qc = QuantumCircuit(register)
    for i in range(gates):
        gate_r = random.randint(0, 4)
        qubit_r = random.randint(0, register - 1)
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


def count_occurrences(lst):
    counts = {}
    for obj in lst:
        if obj not in counts:
            counts[obj] = 1
        else:
            counts[obj] += 1
    return counts


def deltas_to_modifier(deltas, s1, s2):
    elem = []
    count = []
    for delta in deltas:
        if isinstance(delta, Removal):
            instruction = s1[delta.location_index]
            if instruction not in elem:
                elem.append(instruction)
                count.append(-1)
            else:
                idx = elem.index(instruction)
                count[idx] = count[idx] - 1
        else:
            instruction = s2[delta.add_gate_index]
            if instruction not in elem:
                elem.append(instruction)
                count.append(1)
            else:
                idx = elem.index(instruction)
                count[idx] = count[idx] + 1
    counts = {}
    for i in range(len(elem)):
        counts[elem[i]] = count[i]
    # return zip(elem, count)
    return counts


def ordered_sample(diffs):
    a = range(len(diffs))
    b = random.randint(0, len(diffs)-1)
    indices = random.sample(a, b)
    # Use the indices to select the elements from the original list
    # and keep the order of the indices
    sample = [diffs[i] for i in sorted(indices)]
    return sample


if __name__ == '__main__':
    unittest.main()
