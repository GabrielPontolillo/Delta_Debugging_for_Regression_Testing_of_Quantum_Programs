from result_classes import Passed, Failed, Inconclusive
from diff_algorithm import print_edit_sequence


# def dd(c_pass, c_fail, test, source_pass = None, source_fail = None):
#     """Return a pair (C_PASS’, C_FAIL’) such that
#         * C_PASS subseteq C_PASS’ subset C_FAIL’ subseteq C_FAIL holds
#         * C_FAIL’ - C_PASS’ is a minimal difference relevant for TEST."""
#     n = 2  # Initial granularity
#
#     while 1:
#         print("ddloop")
#         assert isinstance(test(c_pass, source_pass, source_fail), Passed)
#         assert isinstance(test(c_fail, source_pass, source_fail), Failed)
#
#         delta = listminus(c_fail, c_pass)
#
#         if n > len(delta):
#             return c_pass, c_fail  # No further minimizing
#
#         deltas = split(delta, n)
#         assert len(deltas) == n
#
#         offset = 0
#         j = 0
#         while j < n:
#             print("loop")
#             i = (j + offset) % n
#             next_c_pass = listunion(c_pass, deltas[i])
#             next_c_fail = listminus(c_fail, deltas[i])
#             print("pass circumstances")
#             print(next_c_pass)
#             print_edit_sequence(next_c_pass,  source_pass, source_fail)
#             print("\n\n")
#             print("fail circumstances")
#             print_edit_sequence(next_c_fail, source_pass, source_fail)
#             print(next_c_fail)
#
#             if isinstance(test(next_c_fail, source_pass, source_fail), Failed) and n == 2:  # (1)
#                 print("1")
#                 c_fail = next_c_fail
#                 n = 2
#                 offset = 0
#                 break
#             elif isinstance(test(next_c_fail, source_pass, source_fail), Passed):  # (2)
#                 print("2")
#                 c_pass = next_c_fail
#                 n = 2
#                 offset = 0
#                 break
#             elif isinstance(test(next_c_pass, source_pass, source_fail), Failed):  # (3)
#                 print("3")
#                 c_fail = next_c_pass
#                 n = 2
#                 offset = 0
#                 break
#             elif isinstance(test(next_c_fail, source_pass, source_fail), Failed):  # (4)
#                 print("4")
#                 c_fail = next_c_fail
#                 n = max(n - - 1, 2)
#                 offset = i
#                 break
#             elif isinstance(test(next_c_pass, source_pass, source_fail), Passed):  # (5)
#                 print("5")
#                 c_pass = next_c_pass
#                 n = max(n - - 1, 2)
#                 offset = i
#                 break
#             else:
#                 j = j + 1  # Try next subset
#
#         if j >= n:  # All tests unresolved
#             if n >= len(delta):
#                 return c_pass, c_fail
#             else:
#                 n = min(n * 2, len(delta))  # Increase granularity


def dd(c_pass, c_fail, test, orig_deltas, source_pass = None, source_fail = None):
    """Return a pair (C_PASS’, C_FAIL’) such that
        * C_PASS subseteq C_PASS’ subset C_FAIL’ subseteq C_FAIL holds
        * C_FAIL’ - C_PASS’ is a minimal difference relevant for TEST."""
    n = 2  # Initial granularity

    while 1:
        assert isinstance(test(c_pass, source_pass, source_fail, orig_deltas), Passed)
        assert isinstance(test(c_fail, source_pass, source_fail, orig_deltas), Failed)

        delta = listminus(c_fail, c_pass)

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
            print("pass circumstances")
            print(next_c_pass)
            print_edit_sequence(next_c_pass,  source_pass, source_fail)
            print("\n\n")
            print("fail circumstances")
            print_edit_sequence(next_c_fail, source_pass, source_fail)
            print(next_c_fail)

            if isinstance(test(next_c_fail, source_pass, source_fail, orig_deltas), Failed) and n == 2:  # (1)
                print("1")
                c_fail = next_c_fail
                n = 2
                offset = 0
                break
            elif isinstance(test(next_c_fail, source_pass, source_fail, orig_deltas), Passed):  # (2)
                print("2")
                c_pass = next_c_fail
                n = 2
                offset = 0
                break
            elif isinstance(test(next_c_pass, source_pass, source_fail, orig_deltas), Failed):  # (3)
                print("3")
                c_fail = next_c_pass
                n = 2
                offset = 0
                break
            elif isinstance(test(next_c_fail, source_pass, source_fail, orig_deltas), Failed):  # (4)
                print("4")
                c_fail = next_c_fail
                n = max(n - - 1, 2)
                offset = i
                break
            elif isinstance(test(next_c_pass, source_pass, source_fail, orig_deltas), Passed):  # (5)
                print("5")
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