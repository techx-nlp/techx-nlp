from __future__ import annotations

from typing import List, Generic, TypeVar, Callable, Type, Any


F = TypeVar('F')
T = TypeVar('T')
class Functor(Generic[F]):

    def fmap(self, f: Callable[[F], T]) -> Functor[T]:
        raise NotImplementedError


class Monad(Functor[F]):

    @staticmethod
    def join(m: Monad[Monad[F]]) -> Monad[F]:
        return m.bind(lambda x: x)

    @classmethod
    def pure(cls: Type[Monad[F]], a: F) -> Monad[F]:
        if cls == Monad:
            raise NotImplementedError

        return cls.pure(a)

    def bind(self, f: Callable[[F], Monad[T]]) -> Monad[T]:
        raise NotImplementedError


ErrorT = TypeVar('ErrorT')
class Either(Generic[ErrorT, F], Monad[F]):

    @staticmethod
    def fail(error: ErrorT) -> Either[ErrorT, F]:
        return Left(error)

    @classmethod
    def pure(cls: Type[Either[ErrorT, F]], a: F) -> Either[ErrorT, F]:
        return Right(a)

    def success(self) -> bool:
        raise NotImplementedError

    def on_fail(self, f: Callable[[ErrorT], None]) -> None:
        raise NotImplementedError

    def item(self) -> F:
        raise NotImplementedError


class Left(Either[ErrorT, F]):

    def __init__(self, error: ErrorT):
        self.left = error

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Left):
            return False

        return self.left == other.left

    def fmap(self, f: Callable[[F], T]) -> Either[ErrorT, T]:
        return Either.fail(self.left)

    def bind(self, f: Callable[[F], Any]) -> Either[ErrorT, T]:
        return Either.fail(self.left)

    def success(self) -> bool:
        return False

    def on_fail(self, f: Callable[[ErrorT], None]) -> None:
        f(self.left)

    def item(self) -> F:
        raise ValueError('Left does not yields an item')

    def __repr__(self):
        return f'Left {self.left}'


class Right(Either[ErrorT, F]):

    def __init__(self, value: F):
        self.right = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Right):
            return False

        return self.right == other.right

    def fmap(self, f: Callable[[F], T]) -> Either[ErrorT, T]:
        return Either.pure(f(self.right))

    def bind(self, f: Callable[[F], Any]) -> Either[ErrorT, T]:
        return f(self.right)

    def success(self) -> bool:
        return True

    def on_fail(self, f: Callable[[ErrorT], None]) -> None:
        pass

    def item(self) -> F:
        return self.right

    def __repr__(self):
        return f'Right {self.right}'