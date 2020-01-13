finished = False
MAX_CANDIDATES = 2


def backtrack(a, k , n):
    c = [0] * MAX_CANDIDATES
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
    print([i for i in range(1, k+1) if a[i]])


def construct_candidates(a, k, n, c, ncandidates):
    c[0] = False
    c[1] = True
    return 2


def make_move(a, k, n):
    pass


def unmake_move(a, k, n):
    pass


def generate_subsets(n):
    buffer = [0] * pow(2, n)
    backtrack(buffer, 0, n)


generate_subsets(3)


