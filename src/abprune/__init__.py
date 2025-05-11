from .abprune import Node, ab_start


def main() -> None:
    tree = Node.from_lists(
        [
            [[[1, -15], [2, 19]], [[18, 23], [4, 3]]],
            [[[2, 1], [7, 8]], [[9, 10], [-2, 5]]],
            [[[-1, -30], [4, 7]], [[20, -1], [-1, -5]]],
        ]
    )

    print("=====MAX=====")
    print()
    ab_start(tree, is_max=True)
    print()

    print("=====MIN=====")
    print()
    ab_start(tree, is_max=False)
    print()
