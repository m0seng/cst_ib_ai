from dataclasses import dataclass
import math


@dataclass(frozen=True, slots=True)
class Node:
    is_leaf: bool
    value: float
    children: list["Node"]

    @classmethod
    def from_lists(cls, l: list | float):
        if isinstance(l, list):
            # branch
            return Node(
                is_leaf=False, value=0, children=[Node.from_lists(c) for c in l]
            )
        else:
            # leaf
            return Node(is_leaf=True, value=l, children=[])


def inprint(depth: int, text: str):
    print(f"{'⋅   ' * depth}{text}")


def pname(is_max: bool):
    return "Max" if is_max else "Min"


def pnum(x: float) -> str:
    if math.isinf(x):
        return "+∞" if x > 0 else "-∞"

    if x > 0:
        return f"+{x}"
    else:
        return f"{x}"


def alphabeta(alpha: float, beta: float, node: Node, depth: int, is_max: bool):
    if node.is_leaf:
        inprint(depth, f"hit leaf {pnum(node.value)}")
        return node.value

    value: float

    inprint(depth, f"{pname(is_max)}: [{pnum(alpha)}, {pnum(beta)}]")

    if is_max:
        value = -math.inf
        for child in node.children:
            value = max(
                value, alphabeta(alpha, beta, child, depth=depth + 1, is_max=False)
            )
            if value >= beta:
                # we will never be allowed to get here
                inprint(
                    depth,
                    f"{pname(is_max)}: could force {pnum(value)}? {pname(not is_max)} says {pnum(beta)}; PRUNE",
                )
                return value  # value still returned, potentially allowing bigger prunes above!
            alpha = max(alpha, value)  # feed value back into rest of search
            inprint(depth, f"{pname(is_max)}: [{pnum(alpha)}, {pnum(beta)}]")

        inprint(depth, f"{pname(is_max)}: can force {pnum(value)}")
        return value

    else:
        value = math.inf
        for child in node.children:
            value = min(
                value, alphabeta(alpha, beta, child, depth=depth + 1, is_max=True)
            )
            if value <= alpha:
                # we will never be allowed to get here
                inprint(
                    depth,
                    f"{pname(is_max)}: could force {pnum(value)}? {pname(not is_max)} says {pnum(alpha)}; PRUNE",
                )
                return value  # value still returned, potentially allowing bigger prunes above!
            beta = min(beta, value)  # feed value back into rest of search
            inprint(depth, f"{pname(is_max)}: [{pnum(alpha)}, {pnum(beta)}]")

        inprint(depth, f"{pname(is_max)}: can force {pnum(value)}")
        return value


def ab_start(node: Node, is_max: bool):
    alphabeta(alpha=-math.inf, beta=math.inf, node=node, depth=0, is_max=is_max)
