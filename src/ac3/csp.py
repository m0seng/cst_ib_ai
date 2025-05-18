from typing import Any, Self
from dataclasses import dataclass
from collections import deque


@dataclass
class CSP[V, T]:
    variables: set[V]
    domains: dict[V, set[T]]
    constraints: dict[tuple[V, V], set[tuple[T, T]]]
    assignments: dict[V, T]


    def sanity_check(self) -> bool:
        # only to be applied on an initial CSP, not children in backtracking

        if self.variables.symmetric_difference(self.domains):
            return False
        
        for (i, j), cs in self.constraints.items():
            if i not in self.variables or j not in self.variables:
                return False
            for (t_i, t_j) in cs:
                if t_i not in self.domains[i] or t_j not in self.domains[j]:
                    return False
        
        return True


    @classmethod
    def copy_of(cls, other: Self):
        # make sure to make copies of the sets within domains!
        # TODO: also need to deep copy constraints or not?
        # doesn't seem like we ever change them...
        return cls(
            variables=other.variables,
            domains={k: v.copy() for k, v in other.domains.items()},
            constraints=other.constraints,
            assignments=other.assignments.copy()
        )
    

    def get_neighbours(self, i: V) -> set[V]:
        neighbours: set[V] = set()
        for (a, b) in self.constraints:
            if i == a:
                neighbours.add(b)
            if i == b:
                neighbours.add(a)
        return neighbours
    

    def get_constraints(self, i: V, j: V) -> set[tuple[T, T]] | None:
        # checks both tuple orders; read-only!
        if (i, j) in self.constraints:
            return self.constraints[(i, j)]
        elif (j, i) in self.constraints:
            return set((t_i, t_j) for (t_j, t_i) in self.constraints[(j, i)])
        else:
            return None


    # assumes that forward checking of some form is in place
    def get_remaining_value_counts(self) -> dict[V, int]:
        return {v: len(dom) for v, dom in self.domains.items()}
    

    # the degree of a variable is how many constraints
    # it is involved in with unassigned variables
    def get_degrees(self) -> dict[V, int]:
        degrees: dict[V, int] = {v: 0 for v in self.variables}
        for (v_1, v_2) in self.constraints:
            if v_1 not in self.assignments:
                degrees[v_2] += 1
            if v_2 not in self.assignments:
                degrees[v_1] += 1
        return degrees
    

    def get_next_variable(self) -> V:
        # use minimum remaining values heuristic first
        # then degree as a tiebreaker
        candidates: set[V] = set(v for v in self.variables if v not in self.assignments)
        
        rvcs = self.get_remaining_value_counts()
        min_rvc = min(rvcs[v] for v in candidates)
        candidates = set(v for v in candidates if rvcs[v] == min_rvc)
        if len(candidates) == 1:
            return candidates.pop()
        
        degrees = self.get_degrees()
        max_degree = max(degrees[v] for v in candidates)
        candidates = set(v for v in candidates if degrees[v] == max_degree)
        
        # even if more than one candidate remains, we just have to return one at this point
        return candidates.pop()
    

    def get_option_count_per_assignment(self, variable: V) -> dict[T, int]:
        counts: dict[T, int] = {t: 0 for t in self.domains[variable]}
        for (v_l, v_r), cs in self.constraints.items():
            if variable == v_l:
                for (t_l, t_r) in cs:
                    if t_l in counts:
                        counts[t_l] += 1
            elif variable == v_r:
                for (t_l, t_r) in cs:
                    if t_r in counts:
                        counts[t_r] += 1
        return counts
    

    def get_value_order(self, variable: V):
        # least constraining value heuristic
        option_counts: dict[T, int] = self.get_option_count_per_assignment(variable)
        return sorted(option_counts, key=lambda t: option_counts[t], reverse=True)
    

    def add_assignment(self, variable: V, value: T) -> bool:
        # return value indicates whether CSP is still consistent
        assert variable in self.variables
        assert variable not in self.assignments
        assert value in self.domains[variable]

        self.assignments[variable] = value
        self.domains[variable] = set((value,))
        return self.ac_3()
    

    # def with_assignment(self, variable: V, value: T) -> Self:
    #     new_csp = type(self).copy_of(self)
    #     new_csp.add_assignment(variable, value)
    #     return new_csp
    

    # def with_assignments(self, assignments: list[tuple[V, T]]) -> Self:
    #     result = self
    #     for variable, value in assignments:
    #         result = result.with_assignment(variable, value)
    #         print(result.domains)
    #     return result
    

    def ac_3(self) -> bool:
        # return value indicates whether CSP is still consistent
        to_check: deque[tuple[V, V]] = deque()

        # add arcs in both directions
        to_check.extend((i, j) for (i, j) in self.constraints)
        to_check.extend((j, i) for (i, j) in self.constraints)

        while to_check:
            (i, j) = to_check.popleft()
            if self.remove_inconsistencies(i, j):
                if not self.domains[i]:
                    return False
                for k in self.get_neighbours(i):
                    if k != j:
                        to_check.append((k, i))
        
        return True
                

    def remove_inconsistencies(self, i: V, j: V) -> bool:
        # return value denotes whether any domain elements of i were removed
        result = False
        constraint_ij = self.get_constraints(i, j)
        assert constraint_ij is not None  # lmao

        new_i_domain: set[T] = set()
        for t_i in self.domains[i]:
            ts_j = set(t_b for (t_a, t_b) in constraint_ij if t_a == t_i and t_b in self.domains[j])
            if not ts_j:
                result = True
            else:
                new_i_domain.add(t_i)
        
        self.domains[i] = new_i_domain
        return result