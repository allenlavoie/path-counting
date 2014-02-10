"""Counts the number of edge-magic labelings in a path."""

import sys
import itertools
from multiprocessing import Pool

MULTIPROCESS = True
NUM_THREADS = 8

# START_PATH_LENGTH >= 2, since N=1 double counts
START_PATH_LENGTH = 2
STOP_PATH_LENGTH = 8

def recursive_count(item_list, expected_sum, partial_sum, first_item):
    """Count the number of labelings, using the labels in item_list,
    which sum to expected_sum. partial_sum indicates a carry-over, and
    only labelings where the last item in the list is greater than
    first_item are counted (to avoid counting a labeling and its
    reverse)."""
    if len(item_list) == 0:
        return 1
    if len([a for a in item_list if a > first_item]) == 0:
        return 0 # All of these will be "reversed" sequences
    total_sum = 0
    for two_permutation in itertools.permutations(item_list, 2):
        if len(item_list) == 2 and first_item > two_permutation[-1]:
            continue # Don't count a sequence and its reverse
        if sum(two_permutation) + partial_sum != expected_sum:
            continue # This seqence can't work
        remainder = item_list - frozenset(two_permutation)
        total_sum += recursive_count(remainder, expected_sum,
                                     two_permutation[1], first_item)
    return total_sum

def worker_proc(arg_tuple):
    return recursive_count(*arg_tuple)

if MULTIPROCESS:
    procpool = Pool(NUM_THREADS)
    map_func = procpool.map
else:
    map_func = map
print 'Length\tLabelings'
for path_length in range(START_PATH_LENGTH, STOP_PATH_LENGTH + 1):
    permute_list = range(1, 2 * path_length + 2)
    list_set = frozenset(permute_list)
    arg_list = []
    def first_k_sum(k):
        """Sum of first k integers"""
        return k * (k + 1) / 2
    lower_bound = (first_k_sum(2*path_length + 1)
                   + first_k_sum(path_length - 1)) / path_length
    upper_bound = (2*first_k_sum(2*path_length + 1)
                   - first_k_sum(path_length + 2)) / path_length
    for three_permutation in itertools.permutations(permute_list, 3):
        if lower_bound <= sum(three_permutation) <= upper_bound:
            arg_list.append((list_set - frozenset(three_permutation),
                             sum(three_permutation), three_permutation[2],
                             three_permutation[0]))
    total_sum = sum(map_func(worker_proc, arg_list))
    print '%d\t%d' % (path_length, total_sum)
    sys.stdout.flush()
