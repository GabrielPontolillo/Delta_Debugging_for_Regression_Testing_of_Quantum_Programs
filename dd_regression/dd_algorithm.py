"""
   A lot of this code is from the 'Why Programs Fail' book from Andreas Zeller
   *Some modifications made
"""
from dd_regression.diff_algorithm import diff
from dd_regression.helper_functions import order_list_by_another_list
from dd_regression.result_classes import Passed, Failed


def dd(c_pass, c_fail, test, source_pass, source_fail, inputs_to_generate, selected_properties, number_of_measurements,
                                                                                    significance_level, logging=False):
    """Return a pair (C_PASS’, C_FAIL’) such that
        * C_PASS subseteq C_PASS’ subset C_FAIL’ subseteq C_FAIL holds
        * C_FAIL’ - C_PASS’ is a minimal difference relevant for TEST."""
    n = 2  # Initial granularity
    offset = 0
    # try:
    if logging:
        print("test pass")
    if not isinstance(test(c_pass, source_pass, source_fail, inputs_to_generate=inputs_to_generate, selected_properties=selected_properties,
                           number_of_measurements=number_of_measurements, significance_level=significance_level), Passed): return [], []

    if logging:
        print("test fail")
    if not isinstance(test(c_fail, source_pass, source_fail, inputs_to_generate=inputs_to_generate, selected_properties=selected_properties,
                           number_of_measurements=number_of_measurements, significance_level=significance_level), Failed): return [], []

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
            if isinstance(test(next_c_pass, source_pass, source_fail, inputs_to_generate=inputs_to_generate, selected_properties=selected_properties,
                           number_of_measurements=number_of_measurements, significance_level=significance_level), Failed) and n == 2:
                if logging:
                    print("Reduce to subset")
                c_fail = next_c_pass
                offset = i
                reduction_found = True
                break
            elif isinstance(test(next_c_fail, source_pass, source_fail, inputs_to_generate=inputs_to_generate, selected_properties=selected_properties,
                           number_of_measurements=number_of_measurements, significance_level=significance_level), Passed) and n == 2:
                if logging:
                    print("Increase to subset")
                c_pass = next_c_fail
                offset = i  # was offset = 0 in original dd()
                reduction_found = True
                break
            elif isinstance(test(next_c_fail, source_pass, source_fail, inputs_to_generate=inputs_to_generate, selected_properties=selected_properties,
                           number_of_measurements=number_of_measurements, significance_level=significance_level), Failed):
                if logging:
                    print("Reduce to complement")
                c_fail = next_c_fail
                n = max(n - 1, 2)
                offset = i
                reduction_found = True
                break
            elif isinstance(test(next_c_pass, source_pass, source_fail, inputs_to_generate=inputs_to_generate, selected_properties=selected_properties,
                           number_of_measurements=number_of_measurements, significance_level=significance_level), Passed):
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


def dd_repeat(passing_circuit, failing_circuit, test, inputs_to_generate, selected_properties, number_of_measurements, significance_level):
    """
    Will repeatedly execute the delta debugging algorithm until the passing deltas cease to pass and fail deltas cease
    to fail, allowing multiple isolated deltas to be retrieved
    :param passing_circuit: the circuit that returns a passing result when tested using the test function
    :param failing_circuit: the circuit that returns a failing result when tested using the test function
    :param test: the test funtion to use
    :return: all isolated failing deltas (will contain artifacts), original calculated deltas
    """
    failing_input_list = [circuitIns for circuitIns in failing_circuit.data]

    passing_input_list = [circuitIns for circuitIns in passing_circuit.data]

    fail_deltas = diff(passing_input_list, failing_input_list)
    pass_deltas = []

    delta_store = []
    loops = len(fail_deltas)
    for i in range(loops):
        print(f"Delta Debugging loop {i}")
        try:
            pass_diff, fail_diff = dd(pass_deltas, fail_deltas, test, passing_input_list, failing_input_list,
                                      inputs_to_generate=inputs_to_generate, selected_properties=selected_properties,
                                      number_of_measurements=number_of_measurements, significance_level=significance_level)

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
            print(f"deltas after loop {delta_store}")
        except AssertionError as e:
            print(repr(e))
            break
    return delta_store, pass_deltas


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
