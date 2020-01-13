finished = False
MAX_CANDIDATES = 2
NMAX = 10000


def backtrack(a, k , n):
    c = [0] * NMAX
    ncandidates = 0

    if is_a_solution(a, k, n):
        process_solution(a, k, n)
    else:
        k = k + 1
        ncandidates = construct_candidates(a, k, n, c, ncandidates)
        for i in range(ncandidates):
            a[k] = c[i]
            make_move(a, k, n)
            backtrack(a, k, n)
            unmake_move(a, k, n)
            if finished:
                return


def is_a_solution(a, k, n):
    return k == n


def process_solution(a, k, n):
    print('%s' % ' '.join([str(a[i]) for i in range(1, k+1)]))


def construct_candidates(a, k, n, c, ncandidates):
    in_perm = [False] * NMAX
    for i in range(k):
        in_perm[a[i]] = True
    candidates_num = 0
    for i in range(1, n+1):
        if not in_perm[i]:
            c[candidates_num] = i
            candidates_num = candidates_num + 1
    return candidates_num


def make_move(a, k, n):
    pass


def unmake_move(a, k, n):
    pass


def generate_permutations(n):
    buffer = [0] * NMAX
    backtrack(buffer, 0, n)


generate_permutations(3)


