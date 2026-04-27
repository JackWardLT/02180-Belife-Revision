from __future__ import annotations

import re
from dataclasses import dataclass

from src.formula import And, Formula, Iff, Implies, Not, Or, Var


_TOKEN_PATTERN = re.compile(r"\s*(<->|->|[()~&|]|[A-Za-z][A-Za-z0-9_]*)")


@dataclass
class _TokenStream:
    tokens: list[str]
    index: int = 0

    def peek(self) -> str | None:
        if self.index >= len(self.tokens):
            return None
        return self.tokens[self.index]

    def consume(self, expected: str | None = None) -> str:
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of input")
        if expected is not None and token != expected:
            raise ValueError(f"Expected '{expected}' but got '{token}'")
        self.index += 1
        return token


def tokenize(text: str) -> list[str]:
    """Tokenize a propositional logic formula string."""

    tokens: list[str] = []
    position = 0
    while position < len(text):
        match = _TOKEN_PATTERN.match(text, position)
        if match is None:
            snippet = text[position : position + 20]
            raise ValueError(f"Invalid token near: {snippet!r}")
        token = match.group(1)
        tokens.append(token)
        position = match.end()

    if not tokens:
        raise ValueError("Empty formula")
    return tokens


def parse_formula(text: str) -> Formula:
    """Parse formula text into an AST using recursive descent."""

    stream = _TokenStream(tokenize(text))
    formula = _parse_iff(stream)
    if stream.peek() is not None:
        raise ValueError(f"Unexpected token: {stream.peek()!r}")
    return formula


def _parse_iff(stream: _TokenStream) -> Formula:
    left = _parse_implies(stream)
    if stream.peek() == "<->":
        stream.consume("<->")
        right = _parse_iff(stream)
        return Iff(left, right)
    return left


def _parse_implies(stream: _TokenStream) -> Formula:
    left = _parse_or(stream)
    if stream.peek() == "->":
        stream.consume("->")
        right = _parse_implies(stream)
        return Implies(left, right)
    return left


def _parse_or(stream: _TokenStream) -> Formula:
    left = _parse_and(stream)
    while stream.peek() == "|":
        stream.consume("|")
        right = _parse_and(stream)
        left = Or(left, right)
    return left


def _parse_and(stream: _TokenStream) -> Formula:
    left = _parse_not(stream)
    while stream.peek() == "&":
        stream.consume("&")
        right = _parse_not(stream)
        left = And(left, right)
    return left


def _parse_not(stream: _TokenStream) -> Formula:
    if stream.peek() == "~":
        stream.consume("~")
        return Not(_parse_not(stream))
    return _parse_atom(stream)


def _parse_atom(stream: _TokenStream) -> Formula:
    token = stream.peek()
    if token is None:
        raise ValueError("Unexpected end of input while reading atom")

    if token == "(":
        stream.consume("(")
        expression = _parse_iff(stream)
        stream.consume(")")
        return expression

    if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", token):
        stream.consume()
        return Var(token)

    raise ValueError(f"Unexpected token: {token!r}")
