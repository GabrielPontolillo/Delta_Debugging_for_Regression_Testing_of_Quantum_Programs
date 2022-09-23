from result_classes import Passed, Failed, Inconclusive
from diff_algorithm import diff, print_edit_sequence
from dd import dd, split, listunion, listminus
from helper_functions import apply_edit_script, circuit_to_list, list_to_circuit
from assertions import assertPhase

from entangle_qiskit_example import qiskit_entangle, qiskit_entangle_circ
from entangle_qiskit_example_after_patch import qiskit_entangle_patched, qiskit_entangle_patched_circ

import itertools
import numpy as np
from typing import List
from qiskit import QuantumCircuit, Aer, execute

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

pi = np.pi
backend = Aer.get_backend('aer_simulator')


# def test_source(changes: List[any], src_pass, src_fail):
#     modified_function = apply_edit_script(changes, src_pass, src_fail)
#     modified_function.append("try:")
#     modified_function.append("    output = " + modified_function[0][4:-1])
#     modified_function.append("except:")
#     modified_function.append("    output = Inconclusive()")
#     modified_function = "\n".join(modified_function)
#     print(modified_function)
#     exec(modified_function, globals())
#     print(output)
#     if isinstance(output, Inconclusive):
#         return output
#     for out in output:
#         if len(output.keys()) == 1 and out == "10":
#             return Passed()
#         else:
#             return Failed()


def test_circuit(changes: List[any], src_pass, src_fail, orig_deltas, log = True):
    changed_circuit_list = apply_edit_script(changes, src_pass, src_fail, orig_deltas)
    changed_circuit = list_to_circuit(changed_circuit_list)

    changed_circuit.measure([0, 1], [0, 1])

    if log:
        print(changed_circuit)

    res = backend.run(changed_circuit).result().get_counts()
    # print(res)
    for out in res:
        if len(res.keys()) == 1 and out == "10":
            return Passed()
        else:
            return Failed()


# def run_src_test():
#     srcfail = inspect.getsource(qiskit_entangle).split("\n")
#     srcpass = inspect.getsource(qiskit_entangle_patched).split("\n")
#
#     fail_deltas = diff(srcpass, srcfail)
#     pass_deltas = []
#
#     passdiff, faildiff = dd(pass_deltas, fail_deltas, test_source, srcpass, srcfail)
#     print("passdiff")
#     print(passdiff)
#     print("faildiff")
#     print(faildiff)
#     print_edit_sequence(passdiff, srcpass, srcfail)
#     print("\n\n\n")
#     print_edit_sequence(faildiff, srcpass, srcfail)
#     print("passing source")
#     print(srcpass)
#     print("failing source")
#     print(srcfail)
#     print("old failing")
#     print("\n".join(apply_edit_script(faildiff, srcpass, srcfail)))
#     print("new passing")
#     print("\n".join(apply_edit_script(passdiff, srcpass, srcfail)))


def dd_repeat(passing_circuit, failing_circuit, test):
    # print(failing_circuit)
    failing_input_list = circuit_to_list(failing_circuit)

    # print(passing_circuit)
    passing_input_list = circuit_to_list(passing_circuit)

    orig_fail_deltas = diff(passing_input_list, failing_input_list)
    # print(orig_fail_deltas)
    # print(apply_edit_script(orig_fail_deltas, passing_input_list, failing_input_list, orig_fail_deltas), 2)

    fail_deltas = orig_fail_deltas
    pass_deltas = []

    delta_store = []
    loops = len(orig_fail_deltas)
    for i in range(loops):
        print(f"#######\n\n Delta Debugging loop {i}\n\n #######")
        try:
            pass_diff, fail_diff = dd(pass_deltas, fail_deltas, test, orig_fail_deltas,
                                      passing_input_list, failing_input_list)

            print("\noriginal failing")
            print(failing_circuit)
            print("\noriginal passing")
            print(passing_circuit)
            print("\nNEW PASS diffs and circuit")
            print(pass_diff)

            print(list_to_circuit(apply_edit_script(pass_diff, passing_input_list,
                                                    failing_input_list, orig_fail_deltas)))

            print("\nNEW FAIL diffs and circuit")
            print(fail_diff)

            print(list_to_circuit(apply_edit_script(fail_diff, passing_input_list,
                                                    failing_input_list, orig_fail_deltas)))

            print(print_edit_sequence(listminus(fail_diff, pass_diff), passing_input_list, failing_input_list))

            min_change = listminus(fail_diff, pass_diff)

            print(f"removed {min_change}")
            print_edit_sequence(min_change, passing_input_list, failing_input_list)
            fail_deltas = listminus(fail_deltas, min_change)
            print(f"added {fail_deltas}")
            pass_deltas = pass_diff
            #orig_fail_deltas = listminus(orig_fail_deltas, min_change)

            delta_store = listunion(delta_store, min_change)
        except AssertionError as e:
            print(e)
            break
    print(delta_store)
    print_edit_sequence(delta_store, passing_input_list, failing_input_list)
    return delta_store, orig_fail_deltas


def further_narrowing(passing_circuit, failing_circuit, delta_store, orig_deltas, test):
    print("\n\n\n In further narrowing \n\n\n")
    assert isinstance(test(delta_store, passing_circuit, failing_circuit, orig_deltas), Failed)
    assert isinstance(test([], passing_circuit, failing_circuit, orig_deltas), Passed)
    delta_store_len = len(delta_store)
    print(delta_store)
    print(delta_store_len)
    passing_deltas = []
    for i in range(delta_store_len - 1):
        print(i + 1)
        for combination in itertools.combinations(delta_store, i+1):
            print("\n")
            #print(test(combination, passing_circuit, failing_circuit, orig_deltas))
            if isinstance(test(combination, passing_circuit, failing_circuit, orig_deltas), Passed):
                print("combination passed")
                print(combination)
                print_edit_sequence(combination, passing_circuit,  failing_circuit)
                for delta in combination:
                    if delta not in passing_deltas:
                        passing_deltas.append(delta)
    delta_store = listminus(delta_store, passing_deltas)
    print("\n\nfailing test")
    print(delta_store)
    test(delta_store, passing_circuit, failing_circuit, orig_deltas)
    print("\n\npassing test")
    print(passing_deltas)
    test(passing_deltas, passing_circuit, failing_circuit, orig_deltas)

    return delta_store


if __name__ == "__main__":
    deltas, orig_fail_deltas = dd_repeat(qiskit_entangle_patched_circ(), qiskit_entangle_circ(), test_circuit)
    # refined_deltas = further_narrowing(qiskit_entangle_patched_circ(), qiskit_entangle_circ(),
    #                                    deltas, orig_fail_deltas, test_circuit)
    # print_edit_sequence(refined_deltas, circuit_to_list(qiskit_entangle_patched_circ()),
    #                     circuit_to_list(qiskit_entangle_circ()))
    # run_src_test()
    # run_circ_test_2()
    # qiskit_entangle_circ()
    # print(qiskit_entangle_patched_circ())
