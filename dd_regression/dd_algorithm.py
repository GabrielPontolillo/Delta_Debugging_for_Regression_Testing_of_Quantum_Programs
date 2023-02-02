"""
   A lot of this code is from the 'Why Programs Fail' book from Andreas Zeller
   *Some modifications made
"""
from dd_regression.result_classes import Passed, Failed, Inconclusive
from dd_regression.helper_functions import circuit_to_list, list_to_circuit
# from dd_regression.diff_algorithm import diff, print_edit_sequence
from dd_regression.diff_algorithm_r import diff, apply_diffs

import itertools


def dd(c_pass, c_fail, test, source_pass, source_fail):
    """Return a pair (C_PASS’, C_FAIL’) such that
        * C_PASS subseteq C_PASS’ subset C_FAIL’ subseteq C_FAIL holds
        * C_FAIL’ - C_PASS’ is a minimal difference relevant for TEST."""
    n = 2  # Initial granularity

    while 1:
        # try:
        print("test pass")
        assert isinstance(test(c_pass, source_pass, source_fail), Passed)
        # except AssertionError as e:
        #     print("one failure for passing circumstances, retrying")
        #     assert isinstance(test(c_pass, source_pass, source_fail, orig_deltas), Passed)

        # print_edit_sequence(c_fail, source_pass, source_fail)
        # try:
        print("test fail")
        assert isinstance(test(c_fail, source_pass, source_fail), Failed)
        # except AssertionError as e:
        #     print("one failure for failing circumstances, retrying")
        #     assert isinstance(test(c_fail, source_pass, source_fail, orig_deltas), Failed)

        delta = listminus(c_fail, c_pass)

        # print(f"n = {n}")
        # print(f"delta = {len(delta)}")
        if n > len(delta):
            return c_pass, c_fail  # No further minimizing

        deltas = split(delta, n)

        assert len(deltas) == n

        offset = 0
        j = 0
        while j < n:
            i = (j + offset) % n
            next_c_pass = listunion(c_pass, deltas[i])
            next_c_fail = listminus(c_fail, deltas[i])

            if isinstance(test(next_c_fail, source_pass, source_fail), Failed) and n == 2:  # (1)
                print("fail test failed 1")
                c_fail = next_c_fail
                n = 2
                offset = 0
                break
            elif isinstance(test(next_c_fail, source_pass, source_fail), Passed):  # (2)
                print("fail test passed 2")
                c_pass = next_c_fail
                n = 2
                offset = 0
                break
            elif isinstance(test(next_c_pass, source_pass, source_fail), Failed):  # (3)
                print("pass test failed 3")
                c_fail = next_c_pass
                n = 2
                offset = 0
                break
            elif isinstance(test(next_c_fail, source_pass, source_fail), Failed):  # (4)
                print("fail test failed 4")
                c_fail = next_c_fail
                n = max(n - - 1, 2)
                offset = i
                break
            elif isinstance(test(next_c_pass, source_pass, source_fail), Passed):  # (5)
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
    failing_input_list = circuit_to_list(failing_circuit)

    passing_input_list = circuit_to_list(passing_circuit)

    fail_deltas = diff(passing_input_list, failing_input_list)
    pass_deltas = []

    delta_store = []
    loops = len(fail_deltas)
    for i in range(loops):
        print(f"Delta Debugging loop {i}")
        try:
            pass_diff, fail_diff = dd(pass_deltas, fail_deltas, test, passing_input_list, failing_input_list)

            min_change = listminus(fail_diff, pass_diff)

            print(f"removed {min_change}")
            fail_deltas = listminus(fail_deltas, min_change)
            print(f"added {fail_deltas}")
            pass_deltas = pass_diff
            delta_store = listunion(delta_store, min_change)
        except AssertionError as e:
            print("assertion error")
            print(repr(e))
            print("failing_circuit")
            print(failing_circuit)
            print("passing_circuit")
            print(passing_circuit)
            break
    print(delta_store)
    return delta_store, pass_deltas


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