# This code is from https://blog.robertelder.org/diff-algorithm/
# https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.4.6927
from dataclasses import dataclass


@dataclass
class Addition:
    # location of gate to insert (from list 2)
    add_gate_index: any
    # location of gate to insert before (from list 1)
    location_index: int


@dataclass
class Removal:
    # location of gate to remove (from list 1)
    location_index: int


@dataclass
class Replace:
    # location of gate to insert (from list 2)
    add_gate_index: any
    # location of gate to replace (from list 1)
    location_index: int


def compute_lcs_len(li1, li2):
    """Computes a table of f(i, j) results."""
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


def diff(li1, li2):
    """Computes the optimal diff of the two given inputs.

  The result is a list where all elements are Removals, Additions or
  Unchanged elements.
  """
    lcs = compute_lcs_len(li1, li2)
    results = []

    i = len(li1)
    j = len(li2)
    # We iterate until we reach the end of both texts.
    while i != 0 or j != 0:
        # If we reached the end of one of text1 (i == 0) or text2 (j == 0),
        # then we just need to print the remaining additions and removals.
        if i == 0:
            print("-")
            print(f"gate add {j - 1}")
            print(f"index add {i}")
            results.append(Addition(j - 1, i))
            j -= 1
        elif j == 0:
            results.append(Removal(i - 1))
            i -= 1
        # Otherwise there's still parts of text1 and text2 left. If the
        # currently considered parts are equal, then we found an unchanged
        # part which belongs to the longest common subsequence.
        elif li1[i - 1] == li2[j - 1]:
            # results.append(Unchanged(li1[i - 1]))
            i -= 1
            j -= 1
        # In any other case, we go in the direction of the longest common
        # subsequence.
        elif lcs[i - 1][j] <= lcs[i][j - 1]:
            results.append(Addition(j - 1, i))
            j -= 1
        else:
            results.append(Removal(i - 1))
            i -= 1

    # Reverse results because we iterated over the texts from the end but
    # want the results to be in forward order.
    return list(reversed(results))


def apply_diffs(li1, li2, diffs):
    res = []
    li1_idx = 0
    for d in diffs:
        print(f"loop {li1_idx}")
        # if current index before first diff's target, add current value in list 1
        while d.location_index > li1_idx:
            res.append(li1[li1_idx])
            li1_idx += 1
        # if current index in diff target, apply diff accordingly
        if d.location_index == li1_idx:
            if isinstance(d, Addition):
                print(d.add_gate_index)
                print(d.location_index)
                res.append(li2[d.add_gate_index])
            elif isinstance(d, Removal):
                li1_idx += 1
            elif isinstance(d, Replace):
                res.append(li2[d.add_gate_index])
                li1_idx += 1
            else:
                raise ValueError("Unrecognized type in diffs")
    # add all values in original list after we went through all diffs
    while li1_idx < len(li1):
        res.append(li1[li1_idx])
        li1_idx += 1
    return res


def convert_deltas_to_replacement(diffs):
    paired_indexes = {}
    for idx, delta in enumerate(diffs):
        # if removal delta, check index of removal + 1 for a matching addition
        if isinstance(delta, Removal):
            for idx2, delta2 in enumerate(diffs[idx:]):
                if isinstance(delta2, Addition):
                    if delta2.location_index == delta.location_index + 1:
                        # if matching addition found, add it to a dictionary
                        paired_indexes[idx] = idx2 + idx
                elif delta2.location_index > delta.location_index + 1:
                    break
    # all items in paired indexes should be unique
    print(paired_indexes)
    new_diffs = []
    for idx, delta in enumerate(diffs):
        # if index is a key in the matched pairs of removal/additions, instead of adding removal, we add a replacement
        if idx in paired_indexes:
            new_diffs.append(Replace(diffs[paired_indexes[idx]].add_gate_index, delta.location_index))
        # if index is in a matched pair (its an addition) and it does not need to be added, as it already is present
        # in the replacement
        elif idx in paired_indexes.values():
            pass
        # if index not matched with any pair, add it
        else:
            new_diffs.append(delta)
    return new_diffs


# replace deltas out should be equal to non replaced version

if __name__ == "__main__":
    t1 = "a"
    t2 = "aaa"
    d = diff(t1, t2)
    print(d)
    print(convert_deltas_to_replacement(d))
    d2 = convert_deltas_to_replacement(d)
    print(apply_diffs(t1, t2, d))
    print(apply_diffs(t1, t2, d2))
