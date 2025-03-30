from typing import overload
from itertools import islice, count

# 에라토스테네스의 체
class Sieve:
    """
    에라토스테네스의 체

    가용 범위를 자동으로 확장하는 에라토스테네스의 체입니다.
    가용 범위를 초과하는 수의 소수 판별이 일어날 때, 자동으로 가용 범위를 두 배로 늘립니다.
    
    *싱글톤 패턴을 통해, 메모리 과사용을 억제하였습니다.*
    """
    _instance = None
    __slots__ = ("_sieve", )

    __BASIC_LIMIT = 1023        # 기본 체 크기

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        self = cls._instance

        return self
    
    def __init__(self) -> None:
        if hasattr(self, "_sieve"):
            return
        
        self._sieve = [False, False] + [True] * (self.__BASIC_LIMIT - 1)
        length = self.__BASIC_LIMIT + 1

        for i in range(length):
            if not self._sieve[i]:
                continue

            for j in range(i*i, length, i):
                self._sieve[j] = False

    def widen(self):
        """
        체 확장 함수

        체의 크기를 두 배로 늘립니다. 일반적으로 내장 호출로 사용됩니다.
        """
        # 더블링 전략을 사용한 업데이트
        length = len(self._sieve)
        self._sieve += [True] * length
        widen_length = length * 2

        for i in range(length):
            if not self._sieve[i]:
                continue

            begin = max(
                i*i,
                (length // i) * i
            )

            for j in range(begin, widen_length, i):
                self._sieve[j] = False

    def narrow(self):
        """
        체 축소 함수

        체의 크기를 절반으로 줄입니다. 필요한 경우 외부에서 호출합니다.
        """
        self._sieve = self._sieve[:len(self._sieve)//2]

    def prime(self, x: int) -> bool:
        """
        소수 판별 함수

        내장된 에라토스테네스의 체를 바탕으로 값이 소수인지 확인합니다.

        Args:
            x: 소수인지 판별할 값

        Returns:
            입력된 값이 소수인가를 반환합니다.

        Example:
        >>> sieve = Sieve()
        >>> sieve.prime(7)
        ... True
        >>> sieve.prime(8)
        ... False
        
        """
        if not isinstance(x, int) or x <= 1:
            return False
        
        while x >= len(self._sieve):
            self.widen()
        
        return self._sieve[x]
    
    @overload
    def __getitem__(self, x: int) -> int:
        """
        `x`번째 소수를 반환하는 함수

        `2`를 `0`번째로 하여, `x`번째 소수를 반환합니다.

        Args:
            x: 원하는 소수의 번째수

        Returns:
            `x`번째 소수
        
        Raises:
            TypeError: `x`가 정수가 아닌 경우
            InfinityAccessError: 무한한 소수열의 맨뒤에서부터 값을 읽으려 시도한 경우(예: `x=-1`)

        Example:
            >>> sieve = Sieve()
            >>> sieve[0]
            ... 2
            >>> sieve[3]
            ... 7
        """
    @overload
    def __getitem__(self, bound: slice) -> list[int]:
        """
        정해진 어느 번째 소수들을 반환하는 함수

        `2`를 `0`번째로 하여, `bound`로 얻어지는 어느 번째 소수들을 리스트로 묶어 반환합니다.

        Args:
            bound: 반환할 소수의 번째수를 정해주는 `slice`

        Returns:
            `bound`에 포함되는 번째수들의 소수를 묶은 리스트
        
        Raises:
            TypeError: `int`형이 아닌 인자로 구성된 `slice`를 입력한 경우
            InfinityAccessError: 무한을 함의하는 `slice`를 범위로 준 경우

        Example:
            >>> sieve = Sieve()
            >>> sieve[:5]
            ... [2, 3, 5, 7, 11]
            >>> sieve[1:9:3]
            ... [3, 11, 19]
        """

    def __getitem__(self, arg: int | slice) -> int | list[int]:
        """
        정해진 어느 번째 소수를 반환하는 함수

        자세한 것은 각 경우의 __doc__를 읽어보시길 권장합니다.
        아래는 각 경우에서 다루지 않은 오류에 대한 정보입니다.

        Raises:
            TypeError: 인자로 `int`나 `slice`가 아닌 다른 형이 전달된 경우
        """
        if isinstance(arg, int):
            start, stop, step = arg, arg+1, 1
        elif isinstance(arg, slice):
            start, stop, step = arg.start, arg.stop, arg.step

            if start is None:
                start = 0
            if step is None:
                step = 1 if start < stop else -1

            if any(
                not isinstance(value, int)
                for value in (start, stop, step)
            ):
                raise TypeError("잘못된 slice 형식입니다.")

            if any([
                stop is None,                       # 한계점을 알 수 없음.
                start < 0 or stop < 0,              # 뒤부터 접근하는 방식을 사용할 수 없음.
                start > stop and step > 0,          # 증가를 통해 한계점에 도달할 수 없음.
                start < stop and step < 0,          # 감소를 통해 한계점에 도달할 수 없음.
            ]):
                raise InfinityAccessError("무한에 접근하려 시도했습니다.")
        else:
            raise TypeError("잘못된 접근 형식입니다.")
            
        decrease = False

        if start > stop:
            decrease = True
            start, stop = stop+1, start+1
            step *= -1

        result = list(islice(filter(lambda x: self.prime(x), count(2)), start, stop, step))

        if decrease:
            result.reverse()

        if isinstance(arg, int):
            return result[0]
        return result

class InfinityAccessError(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg
    def __str__(self) -> str:
        return self.msg