from typing import Literal
from .csp import CSP
from .backtrack import backtrack

type Colour = Literal["R", "C", "B"]

def main():
    colour_pairs: set[tuple[Colour, Colour]] = set((
        ("R", "C"),
        ("R", "B"),
        ("C", "R"),
        ("C", "B"),
        ("B", "R"),
        ("B", "C")
    ))

    edges: set[tuple[int, int]] = set((
        (1, 2), (1, 3), (1, 4),
        (2, 4), (2, 6),
        (3, 4), (3, 7),
        (4, 5),
        (5, 6), (5, 7),
        (6, 7), (6, 8),
        (7, 8)
    ))

    variables: set[int] = set((1, 2, 3, 4, 5, 6, 7, 8))
    domains = {v: set(("R", "C", "B")) for v in variables}
    constraints = {(i, j): colour_pairs for (i, j) in edges}

    # pre_assignments: list[tuple[int, Colour]] = (
    #     (1, "R"),
    #     (4, "C"),
    #     (5, "R"),
    #     (8, "C"),
    #     (6, "B")
    # )

    forced_order: list[int] = [1, 4, 5, 8, 6]
    forced_attempts: dict[int, Colour] = {
        1: "R",
        4: "C",
        5: "R",
        8: "C",
        6: "B"
    }

    csp: CSP[int, Colour] = CSP(
        variables=variables,
        domains=domains,
        constraints=constraints,
        assignments={}
    )

    # backtrack(csp)
    backtrack(csp, forced_order, forced_attempts)