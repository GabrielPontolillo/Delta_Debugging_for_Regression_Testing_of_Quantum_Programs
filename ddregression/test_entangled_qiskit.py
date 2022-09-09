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

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

pi = np.pi
backend = Aer.get_backend('aer_simulator')


## see if we can put an index on the diffs, compare with operations before
## merging diffs

def test_source(changes: List[any], src_pass, src_fail):
    modified_function = apply_edit_script(changes, src_pass, src_fail)
    modified_function.append("try:")
    modified_function.append("    output = " + modified_function[0][4:-1])
    modified_function.append("except:")
    modified_function.append("    output = Inconclusive()")
    modified_function = "\n".join(modified_function)
    print(modified_function)
    exec(modified_function, globals())
    print(output)
    if isinstance(output, Inconclusive):
        return output
    for out in output:
        if len(output.keys()) == 1 and out == "10":
            return Passed()
        else:
            return Failed()


def test_circuit(changes: List[any], src_pass, src_fail, orig_deltas):
    changed_circuit_list = apply_edit_script(changes, src_pass, src_fail, orig_deltas)
    changed_circuit = list_to_circuit(changed_circuit_list, 2)

    changed_circuit.measure([0,1],[0,1])

    print(changed_circuit)

    res = backend.run(changed_circuit).result().get_counts()
    print(res)
    for out in res:
        if len(res.keys()) == 1 and out == "10":
            return Passed()
        else:
            return Failed()


def run_src_test():
    srcfail = inspect.getsource(qiskit_entangle).split("\n")
    srcpass = inspect.getsource(qiskit_entangle_patched).split("\n")

    fail_deltas = diff(srcpass, srcfail)
    pass_deltas = []

    passdiff, faildiff = dd(pass_deltas, fail_deltas, test_source, srcpass, srcfail)
    print("passdiff")
    print(passdiff)
    print("faildiff")
    print(faildiff)
    print_edit_sequence(passdiff, srcpass, srcfail)
    print("\n\n\n")
    print_edit_sequence(faildiff, srcpass, srcfail)
    print("passing source")
    print(srcpass)
    print("failing source")
    print(srcfail)
    print("old failing")
    print("\n".join(apply_edit_script(faildiff, srcpass, srcfail)))
    print("new passing")
    print("\n".join(apply_edit_script(passdiff, srcpass, srcfail)))


# def run_circ_test():
#     failing = qiskit_entangle_circ()
#
#     failing_input_list = circuit_to_list(failing)
#
#     passing = qiskit_entangle_patched_circ()
#
#     passing_input_list = circuit_to_list(passing)
#
#     fail_deltas = diff(passing_input_list, failing_input_list)
#     print(passing_input_list)
#     print(failing_input_list)
#     print_edit_sequence(fail_deltas, passing_input_list, failing_input_list)
#
#     pass_deltas = []
#
#     # print(test_circuit(pass_deltas, passing_input_list, failing_input_list))
#     passdiff, faildiff = dd(pass_deltas, fail_deltas, test_circuit, passing_input_list, failing_input_list)
#
#     print("original failing")
#     print(failing)
#     print("original passing")
#     print(passing)
#     print("new  pass diffs and circuit")
#     print(passdiff)
#
#     print(list_to_circuit(apply_edit_script(passdiff, passing_input_list, failing_input_list), 2))
#
#     print("new fail diffs and circuit")
#     print(faildiff)
#
#     print(list_to_circuit(apply_edit_script(faildiff, passing_input_list, failing_input_list), 2))
#     #print(test_circuit(passdiff, passing_input_list, failing_input_list))
#     #print(test_circuit(faildiff, passing_input_list, failing_input_list))


def run_circ_test_2():
    failing = qiskit_entangle_circ()

    failing_input_list = circuit_to_list(failing)

    passing = qiskit_entangle_patched_circ()

    passing_input_list = circuit_to_list(passing)

    fail_deltas = diff(passing_input_list, failing_input_list)
    print(fail_deltas)
    print(apply_edit_script(fail_deltas, passing_input_list, failing_input_list, fail_deltas), 2)
    #print(list_to_circuit(apply_edit_script(fail_deltas, passing_input_list, failing_input_list), 2))
    #print_edit_sequence(fail_deltas, passing_input_list,  failing_input_list)
    fail_deltas = [(fail_deltas[0], fail_deltas[3]), (fail_deltas[1], fail_deltas[4]), fail_deltas[2]]
    #fail_deltas = [fail_deltas[0], fail_deltas[3], fail_deltas[1], fail_deltas[4], fail_deltas[2]]
    print("\n\n\n")
    #print_edit_sequence(fail_deltas, passing_input_list,  failing_input_list)
    print(apply_edit_script(fail_deltas, passing_input_list, failing_input_list, fail_deltas), 2)
    #print(list_to_circuit(apply_edit_script(fail_deltas, passing_input_list, failing_input_list), 2))

    #fail_deltas = [(fail_deltas[0], fail_deltas[2])]
    #fail_deltas = [(fail_deltas[1], fail_deltas[3])]

    pass_deltas = []

    # print(test_circuit(pass_deltas, passing_input_list, failing_input_list))
    passdiff, faildiff = dd(pass_deltas, fail_deltas, test_circuit, fail_deltas, passing_input_list, failing_input_list)

    print("original failing")
    print(failing)
    print("original passing")
    print(passing)
    print("new  pass diffs and circuit")
    print(passdiff)

    print(list_to_circuit(apply_edit_script(passdiff, passing_input_list, failing_input_list, fail_deltas), 2))

    print("new fail diffs and circuit")
    print(faildiff)

    print(list_to_circuit(apply_edit_script(faildiff, passing_input_list, failing_input_list, fail_deltas), 2))

    min_change = listminus(faildiff, passdiff)
    fail_deltas = listminus(fail_deltas, min_change)
    print(faildiff)
    print([min_change[0][0], min_change[0][1]])
    print(fail_deltas)
    print("min change\n\n")
    print(min_change)
    print_edit_sequence([min_change[0][0], min_change[0][1]], passing_input_list, failing_input_list)
    # passdiff, faildiff = dd(pass_deltas, fail_deltas, test_circuit, passing_input_list, failing_input_list)
    # min_change = listminus(faildiff, passdiff)
    # fail_deltas = listminus(fail_deltas, min_change)
    # print(fail_deltas)



if __name__ == "__main__":
    #run_src_test()
    run_circ_test_2()
    #qiskit_entangle_circ()
    #print(qiskit_entangle_patched_circ())


