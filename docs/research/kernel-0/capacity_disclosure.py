"""Check the finite admission-disclosure results without external dependencies."""

from functools import cache
from itertools import combinations, product


def minimum_partition(size, is_feasible):
    """Enumerate blocks containing a fixed pivot to avoid permutation duplicates."""

    @cache
    def solve(remaining):
        if not remaining:
            return 0
        pivot = remaining & -remaining
        rest = remaining ^ pivot
        best = remaining.bit_count()
        subset = rest
        while subset:
            block = subset | pivot
            if is_feasible(block):
                best = min(best, 1 + solve(remaining ^ block))
            subset = (subset - 1) & rest
        return min(best, 1 + solve(rest))

    return solve((1 << size) - 1)


def graph_minimum(residuals, tolerance):
    conflicts = [
        (1 << left) | (1 << right)
        for left, right in combinations(range(len(residuals)), 2)
        if any(abs(a - b) > gap for a, b, gap in
               zip(residuals[left], residuals[right], tolerance))
    ]
    return minimum_partition(
        len(residuals), lambda block: all(block & edge != edge for edge in conflicts)
    )


def direct_cover_minimum(residuals, tolerance):
    # Enumerate actual allowances and ask the original safety and slack questions.
    allowances = product(*(range(max(axis) + 1) for axis in zip(*residuals)))
    covers = set()
    for allowance in allowances:
        covers.add(sum(
            1 << index for index, residual in enumerate(residuals)
            if all(0 <= r - q <= gap for r, q, gap in
                   zip(residual, allowance, tolerance))
        ))
    covers.discard(0)

    @cache
    def solve(remaining):
        if not remaining:
            return 0
        pivot = remaining & -remaining
        return 1 + min(solve(remaining & ~cover) for cover in covers if cover & pivot)

    return solve((1 << len(residuals)) - 1)


def recover_with_threshold_queries(capacity, fits):
    low, high = 0, capacity
    calls = 0
    while low < high:
        request = (low + high + 1) // 2
        if fits(request):
            low = request
        else:
            high = request - 1
        calls += 1
    return low, calls


def main():
    grid = tuple(product(range(3), repeat=2))
    instances = 0
    for size in range(1, len(grid) + 1):
        for residuals in combinations(grid, size):
            for tolerance in product(range(3), repeat=2):
                assert graph_minimum(residuals, tolerance) == direct_cover_minimum(
                    residuals, tolerance
                ), (residuals, tolerance)
                instances += 1
    print(f"{instances} correlated instances: conflict colorings agree with direct covers")

    boxes = 0
    for cx, cy, dx, dy in product(range(3), repeat=4):
        residuals = tuple(product(range(cx + 1), range(cy + 1)))
        expected = (cx // (dx + 1) + 1) * (cy // (dy + 1) + 1)
        assert direct_cover_minimum(residuals, (dx, dy)) == expected
        boxes += 1
    print(f"{boxes} independent boxes: exact alphabet formula agrees with direct covers")

    threshold_cases = 0
    for capacity in range(129):
        for residual in range(capacity + 1):
            result, calls = recover_with_threshold_queries(
                capacity, lambda request: request <= residual
            )
            assert result == residual and calls <= capacity.bit_length()
            threshold_cases += 1
    print(f"{threshold_cases} scalar cases: exact replies recover the residual")


if __name__ == "__main__":
    main()
