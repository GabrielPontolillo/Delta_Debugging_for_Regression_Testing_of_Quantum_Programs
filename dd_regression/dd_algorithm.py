"""
   Adapted from https://www.debuggingbook.org/html/DeltaDebugger.html#General-Delta-Debugging
"""
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
        print("run passing circumstances test")
        print(f"c_pass {c_pass}")
    if not isinstance(test(c_pass, source_pass, source_fail, inputs_to_generate=inputs_to_generate,
                           selected_properties=selected_properties,
                           number_of_measurements=number_of_measurements, significance_level=significance_level),
                      Passed): return [], []

    if logging:
        print("test failing circumstances test")
        print(f"c_fail {c_fail}")
    if not isinstance(test(c_fail, source_pass, source_fail, inputs_to_generate=inputs_to_generate,
                           selected_properties=selected_properties,
                           number_of_measurements=number_of_measurements, significance_level=significance_level),
                      Failed): return [], []

    while True:
        if logging:
            print(f"in dd loop")
        delta = list_minus(c_fail, c_pass)

        if n > len(delta):
            if logging:
                print(f"n ({n}) < delta length ({delta})")
            return c_pass, c_fail  # No further minimizing

        deltas = split(delta, n)
        # print(deltas)

        reduction_found = False
        j = 0
        # offset = 0
        while j < n:
            i = (j + offset) % n
            next_c_pass = order_list_by_another_list(list_union(c_pass, deltas[i]), c_fail, logging=False)
            next_c_fail = order_list_by_another_list(list_minus(c_fail, deltas[i]), c_fail, logging=False)

            if logging:
                print("passing deltas to test:")
                print(next_c_pass)
                print("failing deltas to test:")
                print(next_c_fail)

            if isinstance(test(next_c_pass, source_pass, source_fail, inputs_to_generate=inputs_to_generate,
                               selected_properties=selected_properties,
                               number_of_measurements=number_of_measurements, significance_level=significance_level),
                          Failed) and n == 2:
                if logging:
                    print("Reduce to subset")
                    print("Pass test failed")
                c_fail = next_c_pass
                offset = i
                reduction_found = True
                break

            elif isinstance(test(next_c_fail, source_pass, source_fail, inputs_to_generate=inputs_to_generate,
                                 selected_properties=selected_properties,
                                 number_of_measurements=number_of_measurements, significance_level=significance_level),
                            Passed) and n == 2:
                if logging:
                    print("Increase to subset")
                    print("Fail Test Passed")
                c_pass = next_c_fail
                offset = i  # was offset = 0 in original dd()
                reduction_found = True
                break
            elif isinstance(test(next_c_fail, source_pass, source_fail, inputs_to_generate=inputs_to_generate,
                                 selected_properties=selected_properties,
                                 number_of_measurements=number_of_measurements, significance_level=significance_level),
                            Failed):
                if logging:
                    print("Reduce to complement")
                    print("Fail test Failed")
                c_fail = next_c_fail
                n = max(n - 1, 2)
                offset = i
                reduction_found = True
                break
            elif isinstance(test(next_c_pass, source_pass, source_fail, inputs_to_generate=inputs_to_generate,
                                 selected_properties=selected_properties,
                                 number_of_measurements=number_of_measurements, significance_level=significance_level),
                            Passed):
                if logging:
                    print("Increase to complement")
                    print("Pass test passed")
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
                print("All tests unresolved")

            if n >= len(delta):
                return c_pass, c_fail

            if logging:
                print("Increase granularity")
            n = min(n * 2, len(delta))


def split(elements, n: int):
    """
    split a list into n (roughly equally sized) sublists
    """
    assert 1 <= n <= len(elements)

    k, m = divmod(len(elements), n)
    try:
        subsets = list(elements[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]
                       for i in range(n))
    except TypeError:
        # Convert to list and back
        subsets = list(type(elements)(
            list(elements)[i * k + min(i, m):(i + 1) * k + min(i + 1, m)])
                       for i in range(n))

    assert len(subsets) == n
    assert sum(len(subset) for subset in subsets) == len(elements)
    assert all(len(subset) > 0 for subset in subsets)

    return subsets


def list_minus(c1, c2):
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


def list_union(c1, c2):
    """Return the union of C1 and C2.
    Assumes elements of C1 are hashable."""
    # The hash map S1 has an entry for each element in C1
    diffs = list_minus(c1, c2)
    return diffs + c2
