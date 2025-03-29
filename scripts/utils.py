from typing import Callable

_StrictlyMonotonicFunction = Callable[[int], int]
_Bound = tuple[int|_StrictlyMonotonicFunction, int|_StrictlyMonotonicFunction]

def inverse(func: _StrictlyMonotonicFunction, *, bound: _Bound = (0, lambda x: x)):
    def inv_function(x: int) -> int:
        left, right = (
            b(x) if callable(b) else b
            for b in bound
        )

        increase = func(left) < func(right)

        if not isinstance(left, int) or not isinstance(right, int):
            raise TypeError("탐색 범위는 int형으로 얻어져야 합니다!")

        past = (left, right)

        while left <= right:
            mid = (left + right) // 2
            expected = func(mid)

            if expected == x:
                return mid
            else:
                if increase:
                    if expected < x:
                        left = mid + 1
                    else:
                        right = mid - 1
                else:
                    if expected < x:
                        right = mid - 1
                    else:
                        right = mid + 1

            if (left, right) == past:
                raise ValueError(f"수렴하는 값을 찾을 수 없습니다. (x={x})")
            past = (left, right)

        return (left + right) // 2
    
    return inv_function

sqrt = inverse(lambda x: x*x)
cbrt = inverse(lambda x: x**3, bound=(lambda x: -abs(x), lambda x: abs(x)))
log2 = inverse(lambda x: 2**x)
log10 = inverse(lambda x: 10**x)