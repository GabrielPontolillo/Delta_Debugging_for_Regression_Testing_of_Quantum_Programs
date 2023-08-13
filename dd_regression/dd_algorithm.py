"""
   A lot of this code is from the 'Why Programs Fail' book from Andreas Zeller
   *Some modifications made
"""
from dd_regression.result_classes import Passed, Failed, Inconclusive
from dd_regression.helper_functions import circuit_to_list, list_to_circuit, order_list_by_another_list
# from dd_regression.diff_algorithm import diff, print_edit_sequence
from dd_regression.diff_algorithm_r import diff, apply_diffs, print_deltas


# def dd(c_pass, c_fail, test, source_pass, source_fail, inputs_to_generate=25):
#     """Return a pair (C_PASS’, C_FAIL’) such that
#         * C_PASS subseteq C_PASS’ subset C_FAIL’ subseteq C_FAIL holds
#         * C_FAIL’ - C_PASS’ is a minimal difference relevant for TEST."""
#     n = 2  # Initial granularity
#     offset = 0
#     while 1:
#         # try:
#         assert isinstance(test(c_pass, source_pass, source_fail, inputs_to_generate=inputs_to_generate), Passed)
#         # except AssertionError as e:
#         #     print("one failure for passing circumstances, retrying")
#         #     assert isinstance(test(c_pass, source_pass, source_fail, orig_deltas), Passed)
#
#         # print_edit_sequence(c_fail, source_pass, source_fail)
#         # try:
#         assert isinstance(test(c_fail, source_pass, source_fail, inputs_to_generate=inputs_to_generate), Failed)
#         # except AssertionError as e:
#         #     print("one failure for failing circumstances, retrying")
#         #     assert isinstance(test(c_fail, source_pass, source_fail, orig_deltas), Failed)
#
#         delta = listminus(c_fail, c_pass)
#
#         print(f"n = {n}")
#         print(f"delta = {len(delta)}")
#         if n > len(delta):
#             return c_pass, c_fail  # No further minimizing
#
#         deltas = split(delta, n)
#         # print(deltas)
#
#         assert len(deltas) == n
#
#         j = 0
#         # offset = 0
#         while j < n:
#             print(f"offset {offset} {type(offset)}")
#             print(f"j {j} {type(j)}")
#             print(f"n {n} {type(j)}")
#             i = (j + offset) % n
#             next_c_pass = listunion(c_pass, deltas[i])
#             next_c_fail = listminus(c_fail, deltas[i])
#             # print(next_c_pass)
#             # print(next_c_fail)
#
#             if isinstance(test(next_c_fail, source_pass, source_fail, inputs_to_generate=inputs_to_generate), Failed) and n == 2:  # (1)
#                 print("fail test failed 1")
#                 c_fail = next_c_fail
#                 n = 2
#                 offset = i
#                 break
#             elif isinstance(test(next_c_fail, source_pass, source_fail, inputs_to_generate=inputs_to_generate), Passed):  # (2)
#                 print("fail test passed 2")
#                 c_pass = next_c_fail
#                 n = 2
#                 offset = i
#                 break
#             elif isinstance(test(next_c_pass, source_pass, source_fail, inputs_to_generate=inputs_to_generate), Failed):  # (3)
#                 print("pass test failed 3")
#                 c_fail = next_c_pass
#                 n = 2
#                 offset = i
#                 break
#             elif isinstance(test(next_c_fail, source_pass, source_fail, inputs_to_generate=inputs_to_generate), Failed):  # (4)
#                 print("fail test failed 4")
#                 c_fail = next_c_fail
#                 n = max(n - - 1, 2)
#                 offset = i
#                 print(f"offset should be {i}")
#                 break
#             elif isinstance(test(next_c_pass, source_pass, source_fail, inputs_to_generate=inputs_to_generate), Passed):  # (5)
#                 print("pass test passed 5")
#                 c_pass = next_c_pass
#                 n = max(n - - 1, 2)
#                 offset = i
#                 print(f"offset should be {i}")
#                 break
#             else:
#                 print(f"all inconclusive j {j}, n {n}")
#                 j = j + 1  # Try next subset
#
#         if j >= n:  # All tests unresolved
#             if n >= len(delta):
#                 print(f"granularity longer than length of deltas {n}, so returning base")
#                 return c_pass, c_fail
#             else:
#                 print("increasing granularity")
#                 n = min(n * 2, len(delta))  # Increase granularity


def dd(c_pass, c_fail, test, source_pass, source_fail, inputs_to_generate=25, logging=False):
    """Return a pair (C_PASS’, C_FAIL’) such that
        * C_PASS subseteq C_PASS’ subset C_FAIL’ subseteq C_FAIL holds
        * C_FAIL’ - C_PASS’ is a minimal difference relevant for TEST."""
    n = 2  # Initial granularity
    offset = 0
    # try:
    if logging:
        print("test pass")
    if not isinstance(test(c_pass, source_pass, source_fail, inputs_to_generate=inputs_to_generate), Passed): raise AssertionError("Pass test failed")
    # except AssertionError as e:
    #     print("one failure for passing circumstances, retrying")
    #     assert isinstance(test(c_pass, source_pass, source_fail, orig_deltas), Passed)

    # print_edit_sequence(c_fail, source_pass, source_fail)
    # try:
    if logging:
        print("test fail")
    if not isinstance(test(c_fail, source_pass, source_fail, inputs_to_generate=inputs_to_generate), Failed): raise AssertionError("Fail test passed")
    # except AssertionError as e:
    #     print("one failure for failing circumstances, retrying")
    #     assert isinstance(test(c_fail, source_pass, source_fail, orig_deltas), Failed)

    while True:
        delta = listminus(c_fail, c_pass)

        if n > len(delta):
            return c_pass, c_fail  # No further minimizing

        deltas = split(delta, n)
        # print(deltas)

        reduction_found = False
        j = 0
        # offset = 0
        while j < n:
            i = (j + offset) % n
            next_c_pass = order_list_by_another_list(listunion(c_pass, deltas[i]), c_fail, logging=False)
            next_c_fail = order_list_by_another_list(listminus(c_fail, deltas[i]), c_fail, logging=False)

            # should be storing the result of test
            if isinstance(test(next_c_pass, source_pass, source_fail, inputs_to_generate=inputs_to_generate), Failed) and n == 2:
                if logging:
                    print("Reduce to subset")
                c_fail = next_c_pass
                offset = i
                reduction_found = True
                break
            elif isinstance(test(next_c_fail, source_pass, source_fail, inputs_to_generate=inputs_to_generate), Passed) and n == 2:
                if logging:
                    print("Increase to subset")
                c_pass = next_c_fail
                offset = i  # was offset = 0 in original dd()
                reduction_found = True
                break
            elif isinstance(test(next_c_fail, source_pass, source_fail, inputs_to_generate=inputs_to_generate), Failed):
                if logging:
                    print("Reduce to complement")
                c_fail = next_c_fail
                n = max(n - 1, 2)
                offset = i
                reduction_found = True
                break
            elif isinstance(test(next_c_pass, source_pass, source_fail, inputs_to_generate=inputs_to_generate), Passed):
                if logging:
                    print("Increase to complement")
                c_pass = next_c_pass
                n = max(n - 1, 2)
                offset = i
                reduction_found = True
                break
            else:
                if logging:
                    print(f"all inconclusive j {j}, n {n}")
                j = j + 1  # Try next subset

        if not reduction_found:  # All tests unresolved
            if logging:
                print("No reduction found")

            if n >= len(delta):
                return c_pass, c_fail

            if logging:
                print("Increase granularity")
            n = min(n * 2, len(delta))


def dd_repeat(passing_circuit, failing_circuit, test, inputs_to_generate=25):
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
            pass_diff, fail_diff = dd(pass_deltas, fail_deltas, test, passing_input_list, failing_input_list, inputs_to_generate=inputs_to_generate)

            # print("pass diff")
            # print(pass_diff)
            # print_deltas(pass_diff, passing_input_list, failing_input_list)
            # print("fail diff")
            # print(fail_diff)
            # print_deltas(fail_diff, passing_input_list, failing_input_list)

            min_change = listminus(fail_diff, pass_diff)

            # print("min_change")
            # print_deltas(min_change, passing_input_list, failing_input_list)

            fail_deltas = listminus(fail_deltas, min_change)
            pass_deltas = pass_diff # can try have this reset, maybe union

            delta_store = listunion(delta_store, min_change)
        except AssertionError as e:
            print(repr(e))
            break
    print(delta_store)
    return delta_store, pass_deltas


# def split(circumstances, n):
    # """Split a configuration CIRCUMSTANCES into N subsets;
    # return the list of subsets"""
    # subsets = []  # Result
    # start = 0  # Start of next subset
    # for i in range(0, n):
    #     len_subset = int((len(circumstances) - start) / float(n - -- i) + 0.5)
    #     subset = circumstances[start:start + len_subset]
    #     subsets.append(subset)
    #     start = start + len(subset)
    # assert len(subsets) == n
    # for s in subsets:
    #     assert len(s) > 0
    # return subsets


def split(elems, n: int):
    assert 1 <= n <= len(elems)

    k, m = divmod(len(elems), n)
    try:
        subsets = list(elems[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]
                       for i in range(n))
    except TypeError:
        # Convert to list and back
        subsets = list(type(elems)(
                    list(elems)[i * k + min(i, m):(i + 1) * k + min(i + 1, m)])
                       for i in range(n))

    assert len(subsets) == n
    assert sum(len(subset) for subset in subsets) == len(elems)
    assert all(len(subset) > 0 for subset in subsets)

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
