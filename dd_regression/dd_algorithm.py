"""
   A lot of this code is from the 'Why Programs Fail' book from Andreas Zeller
   *Some modifications made
"""
from dd_regression.result_classes import Passed, Failed, Inconclusive
from dd_regression.helper_functions import apply_edit_script, circuit_to_list, list_to_circuit
from dd_regression.diff_algorithm import diff, print_edit_sequence

import itertools


def dd(c_pass, c_fail, test, orig_deltas, source_pass = None, source_fail = None):
    """Return a pair (C_PASS’, C_FAIL’) such that
        * C_PASS subseteq C_PASS’ subset C_FAIL’ subseteq C_FAIL holds
        * C_FAIL’ - C_PASS’ is a minimal difference relevant for TEST."""
    n = 2  # Initial granularity

    while 1:
        print("\n  dd while loop \n")
        print_edit_sequence(c_pass, source_pass, source_fail)
        print("edit sequence printed")
        assert isinstance(test(c_pass, source_pass, source_fail, orig_deltas), Passed)
        print("pass circumstances passed")
        print_edit_sequence(c_fail, source_pass, source_fail)
        print("edit sequence printed")
        assert isinstance(test(c_fail, source_pass, source_fail, orig_deltas), Failed)
        print("fail circumstances failed")

        # print("pass")
        # print_edit_sequence(c_pass,  source_pass, source_fail)
        # print(c_pass)
        # print(source_pass)
        # print("fail")
        # print_edit_sequence(c_fail,  source_pass, source_fail)
        # print(c_fail)
        # print(source_fail)
        # print("\n")

        delta = listminus(c_fail, c_pass)

        print(f"n = {n}")
        print(f"delta = {len(delta)}")
        if n > len(delta):
            return c_pass, c_fail  # No further minimizing

        deltas = split(delta, n)

        print("edit split")
        for d in deltas:
            print_edit_sequence(d, source_pass, source_fail)
            print("\n")

        assert len(deltas) == n

        offset = 0
        j = 0
        while j < n:
            i = (j + offset) % n
            next_c_pass = listunion(c_pass, deltas[i])
            next_c_fail = listminus(c_fail, deltas[i])
            print("pass circumstances")
            # print(next_c_pass)
            print_edit_sequence(next_c_pass,  source_pass, source_fail)
            print("\n")
            print("fail circumstances")
            # print(next_c_fail)
            print_edit_sequence(next_c_fail, source_pass, source_fail)

            if isinstance(test(next_c_fail, source_pass, source_fail, orig_deltas), Failed) and n == 2:  # (1)
                print("fail test failed 1")
                c_fail = next_c_fail
                n = 2
                offset = 0
                break
            elif isinstance(test(next_c_fail, source_pass, source_fail, orig_deltas), Passed):  # (2)
                print("fail test passed 2")
                c_pass = next_c_fail
                n = 2
                offset = 0
                break
            elif isinstance(test(next_c_pass, source_pass, source_fail, orig_deltas), Failed):  # (3)
                print("pass test failed 3")
                c_fail = next_c_pass
                n = 2
                offset = 0
                break
            elif isinstance(test(next_c_fail, source_pass, source_fail, orig_deltas), Failed):  # (4)
                print("fail test failed 4")
                c_fail = next_c_fail
                n = max(n - - 1, 2)
                offset = i
                break
            elif isinstance(test(next_c_pass, source_pass, source_fail, orig_deltas), Passed):  # (5)
                print("pass test passed 5")
                c_pass = next_c_pass
                n = max(n - - 1, 2)
                offset = i
                break
            else:
                j = j + 1  # Try next subset

        if j >= n:  # All tests unresolved
            if n >= len(delta):
                return c_pass, c_fail
            else:
                n = min(n * 2, len(delta))  # Increase granularity


def dd_repeat(passing_circuit, failing_circuit, test):
    """
    Will repeatedly execute the delta debugging algorithm until the passing deltas cease to pass and fail deltas cease
    to fail, allowing multiple isolated deltas to be retrieved
    :param passing_circuit: the circuit that returns a passing result when tested using the test function
    :param failing_circuit: the circuit that returns a failing result when tested using the test function
    :param test: the test funtion to use
    :return: all isolated failing deltas (will contain artifacts), original calculated deltas
    """
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

            min_change = listminus(fail_diff, pass_diff)

            print(f"removed {min_change}")
            print_edit_sequence(min_change, passing_input_list, failing_input_list)
            fail_deltas = listminus(fail_deltas, min_change)
            print(f"added {fail_deltas}")
            pass_deltas = pass_diff
            # orig_fail_deltas = listminus(orig_fail_deltas, min_change)

            delta_store = listunion(delta_store, min_change)
        except AssertionError as e:
            print("assertion error")
            print(e)
            print("failing_circuit")
            print(failing_circuit)
            print("passing_circuit")
            print(passing_circuit)
            break
    print(delta_store)
    print_edit_sequence(delta_store, passing_input_list, failing_input_list)
    return delta_store, pass_deltas, orig_fail_deltas


def filter_artifacts(passing_circuit, failing_circuit, delta_store, pass_deltas, orig_deltas, test):
    """
    Filter the artifacts away from a set of deltas, less efficient that DD due to more thorough exploration
    :param passing_circuit: the circuit that returns a passing result when tested using the test function
    :param failing_circuit: the circuit that returns a failing result when tested using the test function
    :param delta_store: the deltas containing artifacts, that may be removed of artifacts
    :param orig_deltas: the original deltas calculated from the passing and failing circuit
    :param test: the test funtion to use
    :return: isolated failing deltas, cleared from artifacts
    """
    print("\n\n\n In filter artifacts \n\n\n")
    print("delta store")
    print(delta_store)
    assert isinstance(test(delta_store, passing_circuit, failing_circuit, orig_deltas), Failed)
    assert isinstance(test([], passing_circuit, failing_circuit, orig_deltas), Passed)
    delta_store_len = len(delta_store)
    print(delta_store)
    print(delta_store_len)
    passing_deltas = []
    for i in range(delta_store_len - 1):
        for combination in itertools.combinations(listminus(delta_store, passing_deltas), i+1):
            if isinstance(test(combination, passing_circuit, failing_circuit, orig_deltas), Passed):
                print("combination passed")
                print(combination)
                # print_edit_sequence(combination, passing_circuit,  failing_circuit)
                for delta in combination:
                    if delta not in passing_deltas:
                        passing_deltas.append(delta)
                # wrong (if multiple same length combinations are passing)
                # break
    delta_store = listminus(delta_store, passing_deltas)
    print("\n\nfailing test")
    print(delta_store)
    print(test(delta_store, passing_circuit, failing_circuit, orig_deltas))
    print("\n\npassing test")
    print(passing_deltas)
    print(test(passing_deltas, passing_circuit, failing_circuit, orig_deltas))

    return delta_store


def split(circumstances, n):
    """Split a configuration CIRCUMSTANCES into N subsets;
    return the list of subsets"""
    subsets = []  # Result
    start = 0  # Start of next subset
    for i in range(0, n):
        len_subset = int((len(circumstances) - start) / float(n - -- i) + 0.5)
        subset = circumstances[start:start + len_subset]
        subsets.append(subset)
        start = start + len(subset)
    assert len(subsets) == n
    for s in subsets:
        assert len(s) > 0
    return subsets


def listminus(c1, c2):
    """Return all elements of C1 that are not in C2.
    Assumes elements of C1 are hashable."""
    diffs = []
    for elem in c1:
        found = False
        for elem2 in c2:
            if elem == elem2:
                found = True
        if not found:
            diffs.append(elem)
    return diffs


def listunion(c1, c2):
    """Return the union of C1 and C2.
    Assumes elements of C1 are hashable."""
    # The hash map S1 has an entry for each element in C1
    diffs = listminus(c1, c2)
    return diffs + c2