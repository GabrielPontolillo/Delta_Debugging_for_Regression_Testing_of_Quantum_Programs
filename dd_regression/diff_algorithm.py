# This code is from https://blog.robertelder.org/diff-algorithm/
# https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.4.6927
import time
from dataclasses import dataclass
from case_studies.mined.quantum_teleportation.quantum_teleportation import QuantumTeleportationMined
from dd_regression.helper_functions import list_to_circuit


@dataclass(eq=True, frozen=True)
class Addition:
    # location of gate to insert before (from list 1)
    location_index: int
    # location of gate to insert (from list 2)
    add_gate: any


@dataclass(eq=True, frozen=True)
class Removal:
    # location of gate to remove (from list 1)
    location_index: int


@dataclass
class Experiment:
    p_value: float
    input_state: []


def compute_lcs_len(li1, li2, diagnostic=False, timeit=False):
    """Computes a table of f(i, j) results."""
    t1 = time.time()
    n = len(li1)
    m = len(li2)

    # We store the results in a (n + 1) x (m + 1) matrix. The +1s are to
    # allocate space for the empty strings. Cell [i][j] will cache the
    # result of f(i, j).
    lcs = [[None for _ in range(m + 1)]
           for _ in range(n + 1)]

    # We then fill the matrix by going through all rows, using the fact
    # that each call only needs results from the previous (i - 1) or
    # same (i) row, and from the previous (j - 1) or same (j) column.
    for i in range(0, n + 1):
        for j in range(0, m + 1):
            # The remaining code is exactly the same recursion as before, but
            # we do not make recursive calls and instead use the results cached
            # in the matrix.
            if i == 0 or j == 0:
                lcs[i][j] = 0
            elif li1[i - 1] == li2[j - 1]:
                lcs[i][j] = 1 + lcs[i - 1][j - 1]
            else:
                lcs[i][j] = max(lcs[i - 1][j], lcs[i][j - 1])
    t2 = time.time()
    if timeit:
        print(f"time_taken compute lcs len for apply diffs= {t2 - t1}")
    return lcs


def find_lcs_list(li1, li2):
    """Finds the longest common subsequence of the given texts."""
    result = []
    lcs = compute_lcs_len(li1, li2)

    i = len(li1)
    j = len(li2)

    # We iterate until we reach the end of text1 (i == 0) or text2 (j == 0)
    while i != 0 and j != 0:
        # If the parts of text1 and text2 that we consider are equal, then we
        # can record this as part of the LCS, and move to i-1, j-1 since this
        # is also how compute_lcs_len traversed.
        if li1[i - 1] == li2[j - 1]:
            result.append(li1[i - 1])
            i -= 1
            j -= 1
        # Otherwise, compute_lcs_len went into the max direction, which is
        # also what we do here.
        elif lcs[i - 1][j] <= lcs[i][j - 1]:
            j -= 1
        else:
            i -= 1

    # Reverse results because we iterated over the texts from the end but
    # want the results to be in forward order.
    return reversed(result)


def diff(li1, li2, diagnostic=False, timeit=False):
    """Computes the optimal diff of the two given inputs.

  The result is a list where all elements are Removals, Additions or
  Unchanged elements.
  """
    if diagnostic:
        print(f"input 1: {li1}")
        print(f"input 2: {li2}")
    lcs = compute_lcs_len(li1, li2)
    results = []
    t1 = time.time()

    i = len(li1)
    j = len(li2)
    # We iterate until we reach the end of both texts.
    while i != 0 or j != 0:
        # If we reached the end of one of text1 (i == 0) or text2 (j == 0),
        # then we just need to print the remaining additions and removals.
        if i == 0:
            if diagnostic:
                print("-")
                print(f"gate add {j - 1}")
                print(f"index add {i}")
            results.append(Addition(i, li2[j - 1]))
            j -= 1
        elif j == 0:
            results.append(Removal(i - 1))
            i -= 1
        # Otherwise there's still parts of text1 and text2 left. If the
        # currently considered parts are equal, then we found an unchanged
        # part which belongs to the longest common subsequence.
        elif li1[i - 1] == li2[j - 1]:
            i -= 1
            j -= 1
        # In any other case, we go in the direction of the longest common
        # subsequence.
        elif lcs[i - 1][j] <= lcs[i][j - 1]:
            results.append(Addition(i, li2[j - 1]))
            j -= 1
        else:
            results.append(Removal(i - 1))
            i -= 1

    # Reverse results because we iterated over the texts from the end but
    # want the results to be in forward order.
    t2 = time.time()
    if timeit:
        print(f"time_taken for diffing = {t2 - t1}")
    return list(reversed(results))


def apply_diffs(li1, diffs, diagnostic=False, timeit=False):
    if diagnostic:
        print(f"input 1:")
        print(list_to_circuit(li1))
        print(f"diffs:")
        print_deltas(li1, diffs)

    t1 = time.time()
    res = []
    li1_idx = 0
    for d in diffs:
        if diagnostic:
            pass
            # print(f"index {li1_idx}")
        # if current index before first diff's target, add current value in list 1
        while d.location_index > li1_idx:
            if diagnostic:
                pass
                # print(f"while loop first {li1_idx}, location {d.location_index}")
            res.append(li1[li1_idx])
            li1_idx += 1
        # if current index in diff target, apply diff accordingly
        if d.location_index == li1_idx:
            if isinstance(d, Addition):
                if diagnostic:
                    pass
                    # print(f"adding gate {d.add_gate_index} at {d.location_index}")
                res.append(d.add_gate)
            elif isinstance(d, Removal):
                if diagnostic:
                    pass
                    # print(f"removing gate at {d.location_index}")
                li1_idx += 1
            else:
                raise ValueError("Unrecognized type in diffs")

    # add all values in original list after we went through all diffs
    while li1_idx < len(li1):
        if diagnostic:
            pass
            # print(f"final while {li1_idx} < {len(li1)}")
        res.append(li1[li1_idx])
        li1_idx += 1
    t2 = time.time()
    if timeit:
        print(f"time_taken for apply diffs= {t2 - t1}")
    if diagnostic:
        print("output circuit")
        print(list_to_circuit(res))
    return res


def print_deltas(li1, diffs):
    for i in range(len(diffs)):
        if isinstance(diffs[i], Removal):
            print(f"remove {li1[diffs[i].location_index]} at {diffs[i].location_index}")
        elif isinstance(diffs[i], Addition):
            print(f"add {diffs[i].add_gate} at {diffs[i].location_index}")


# replace deltas out should be equal to non replaced version
if __name__ == "__main__":
    t1 = "ABAB"
    t2 = "ABBBB"
    d = diff(t1, t2)
    print(d)
    print(d[1])
    print(apply_diffs(t1, d))
