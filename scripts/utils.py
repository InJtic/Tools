from typing import Callable

_StrictlyMonotonicFunction = Callable[[int], int]
_Bound = tuple[int|_StrictlyMonotonicFunction, int|_StrictlyMonotonicFunction]

# 의사 역함수 생성기
def inverse(
        func: _StrictlyMonotonicFunction, 
        *, 
        bound: _Bound = (0, lambda x: x),
        domain: tuple[int, int] = (..., ...)
):
    """
    의사 역함수 생성기.

    입력 `x`에 대해, `y`가 `func(y) = x`를 만족한다고 할 때,
    `n <= y < n+1`인 `n`을 반환하는 함수를 반환합니다.
    역함수의 바닥함수로 이해할 수 있습니다.

    *이진 탐색을 기반으로 제작되었습니다.*

    **`__name__`, `__doc__` 등이 자동으로 설정되지 않음에 주의하십시오.**

    Args:
        func: 의사 역함수로 변환할 함수. 반드시 **강한 단조 함수**여야 합니다.
        bound: 이진 탐색으로 `n`을 탐색할 범위. 입력값 `x`에 대해 반응적이도록 함수를 사용해 설계할 수도 있습니다.
        domain: 의사 역함수의 정의역. 입력값 `x`가 정의역에 포함되지 않으면 탐색 없이 반드시 예외를 발생시킵니다. 
                `...`을 통해 무한대를 표현할 수 있습니다.

    Returns:
        inv_function: 얻어진 의사 역함수.
    
    Raises:
        TypeError: 입력값 `x`가 `int`형이 아닌 경우 발생합니다.
        DomainError: 입력값 `x`가 `domain`에 포함되지 않는 경우 발생합니다.
        TypeError: 탐색 범위 `bound`가 `int`형이나, `int`형을 리턴하는 함수로 이루어지지 않은 경우 발생합니다.
        NothingFoundError: 수렴하는 값 `n`을 찾을 수 없을 때 발생합니다.

    
    위의 예외들은 모두 `inv_function`에서 일어나는 것이지만, 함수 설계에서 참고해야 하므로, 이곳에 정리합니다.

    Example:
        >>> sqrt = inverse(
        ...     lambda x: x*x, 
        ...     bound=(
        ...         0,
        ...         lambda x: x
        ...     ),
        ...     domain=(0, ...)
        ... )
        >>> sqrt(8)
        ... 2
    """
    def inv_function(x: int) -> int:
        if not isinstance(x, int):
            raise TypeError(f"int형이 아닌 인자가 x로 설정되었습니다.")

        dom_left, dom_right = domain

        if (dom_left is not ... and x < dom_left) or (dom_right is not ... and x > dom_right):
            if dom_left is ...: dom_left = "-inf"
            if dom_right is ...: dom_right = "inf"
            raise DomainError(f"정의역에 포함되지 않는 값이 주어졌습니다! ({x} not in [{dom_left}, {dom_right}])")

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
                        left = mid + 1

            if (left, right) == past:
                raise NothingFoundError(f"수렴하는 값을 찾을 수 없습니다. (x={x})")
            past = (left, right)

        return (left + right) // 2
    
    return inv_function

class DomainError(Exception):
    """정의역에 포함되지 않는 값이 주어진 오류"""
    def __init__(self, msg: str) -> None: 
        self.msg = msg

    def __str__(self) -> str:
        return self.msg
    
class NothingFoundError(Exception):
    """탐색 알고리즘에서 아무것도 찾지 못해 발생하는 오류"""
    def __init__(self, msg: str) -> None:
        self.msg = msg

    def __str__(self) -> str:
        return self.msg

# 의사 제곱근 함수
sqrt = inverse(
    lambda x: x*x, 
    bound=(
        0,
        lambda x: x
    ),
    domain=(0, ...)
)
sqrt.__name__ = "sqrt"
sqrt.__doc__ = "의사 제곱근 함수"

# 의사 세제곱근 함수
cbrt = inverse(
    lambda x: x*x*x,
    bound=(
        lambda x: -abs(x),
        lambda x:  abs(x)
    ),
    domain=(..., ...)
)
cbrt.__name__ = "cbrt"
cbrt.__doc__ = "의사 세제곱근 함수"

# 의사 밑이 2인 로그 함수
log2 = inverse(
    lambda x: 2**x,
    bound=(
        0,
        lambda x: x
    ),
    domain=(1, ...)
)
log2.__name__ = "log2"
log2.__doc__ = "의사 밑이 2인 로그 함수"