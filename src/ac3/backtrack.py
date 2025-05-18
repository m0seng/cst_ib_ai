from .csp import CSP

def inprint(depth: int, text: str):
    print(f"{".   " * depth}{text}")

def backtrack[V, T](
        csp: CSP[V, T],
        forced_order: list[V] | None = None,
        forced_attempts: dict[V, T] | None = None
):
    depth = len(csp.assignments)
    if depth == 0:
        inprint(depth=depth, text=csp.str_of_assignments())
        inprint(depth=depth, text=csp.str_of_domains())
        print()

    if len(csp.assignments) == len(csp.variables):
        return csp.assignments
    
    if forced_order is not None and len(forced_order) > depth:
        next_var = forced_order[depth]
    else:
        next_var = csp.get_next_variable()
    
    value_order = csp.get_value_order(next_var)
    if forced_attempts is not None and next_var in forced_attempts:
        attempt = forced_attempts[next_var]
        if attempt in value_order:
            value_order.remove(attempt)
            value_order.insert(0, attempt)

    for t in value_order:
        child_csp = CSP.copy_of(csp)
        is_consistent = child_csp.add_assignment(next_var, t)
        inprint(depth=depth+1, text=child_csp.str_of_assignments())
        inprint(depth=depth+1, text=child_csp.str_of_domains())
        print()
        if not is_consistent:
            continue

        solution: dict[V, T] = backtrack(child_csp, forced_order, forced_attempts)
        if solution is not None:
            return solution
    
    return None