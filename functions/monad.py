from typing import Generic, Callable, Optional, TypeVar

T = TypeVar('T')
U = TypeVar('U')

class Maybe(Generic[T]):
    def __init__(self, value: Optional[T]):
        self.value = value

    def bind(self, func: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        """
        Applies the function `func` to the value if it exists.
        Otherwise, it propagates the None state.
        """
        if self.value is None:
            return Maybe(None)
        return func(self.value)

    def map(self, func: Callable[[T], U]) -> 'Maybe[U]':
        """
        Applies the function to the value if it exists and wraps the result back in a Maybe.
        """
        if self.value is None:
            return Maybe(None)
        return Maybe(func(self.value))
    
    def __repr__(self):
        return f"Just({self.value})" if self.value is not None else "Nothing"
