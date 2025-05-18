from typing import Self
from dataclasses import dataclass
from collections import deque


@dataclass
class CSP[V, T]:
    """
    Represents a constraint satisfaction problem, including variable assignments.

    This is mutable; a backtracking algorithm should make child copies with copy_of().
    """

    variables: set[V]
    domains: dict[V, set[T]]
    constraints: dict[tuple[V, V], set[tuple[T, T]]]
    assignments: dict[V, T]


    def str_of_domains(self):
        """Returns compact string representation of domains."""
        return " ".join(f"{v}({"".join(ts)})" for v, ts in self.domains.items())


    def str_of_assignments(self):
        """Returns compact string representation of assignments."""
        return " ".join(f"{v}={t}" for v, t in self.assignments.items())


    def sanity_check(self) -> bool:
        """
        Checks a CSP without any assignments for correct initialisation
        of variables, domains and constraints.
        """
        assert not self.assignments

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
        """
        Returns a copy of a CSP; to be used in backtracking algorithms.
        """
        # make sure to make copies of the sets within domains!
        # TODO: do we also need to deep copy constraints or not?
        # doesn't seem like we ever change them...
        return cls(
            variables=other.variables,
            domains={k: v.copy() for k, v in other.domains.items()},
            constraints=other.constraints,
            assignments=other.assignments.copy()
        )
    

    def get_neighbours(self, variable: V) -> set[V]:
        """Gets the constraint neighbours of a variable."""
        neighbours: set[V] = set()
        for (a, b) in self.constraints:
            if variable == a:
                neighbours.add(b)
            if variable == b:
                neighbours.add(a)
        return neighbours
    

    def get_constraints(self, i: V, j: V) -> set[tuple[T, T]] | None:
        """
        Gets (a copy of) the allowable set of values in the constraint
        between a directed variable pair, if one exists.
        """
        # check both tuple orders!
        if (i, j) in self.constraints:
            return self.constraints[(i, j)]
        elif (j, i) in self.constraints:
            return set((t_i, t_j) for (t_j, t_i) in self.constraints[(j, i)])
        else:
            return None


    def get_remaining_value_counts(self) -> dict[V, int]:
        """Gets the number of remaining possible assignments for all variables."""
        # assumes that forward checking of some form is in place
        return {v: len(dom) for v, dom in self.domains.items()}
    

    def get_degrees(self) -> dict[V, int]:
        """
        Gets the degrees of all variables.

        The degree of a variable is how many constraints it is involved in with unassigned variables.
        """
        degrees: dict[V, int] = {v: 0 for v in self.variables}
        for (v_1, v_2) in self.constraints:
            if v_1 not in self.assignments:
                degrees[v_2] += 1
            if v_2 not in self.assignments:
                degrees[v_1] += 1
        return degrees
    

    def get_next_variable(self) -> V:
        """
        Heuristic for next variable to try in a backtracking search.

        Applies the minimum remaining values heuristic first,
        then uses degree as a tiebreaker.
        """
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
        """
        Gets the total number of options for neighbours
        allowed by each possible assignment to a variable.
        """
        # checks for neighbours' domains might not be strictly necessary for LCV?
        counts: dict[T, int] = {t: 0 for t in self.domains[variable]}
        for (v_l, v_r), cs in self.constraints.items():
            if variable == v_l:
                for (t_l, t_r) in cs:
                    if t_l in counts and t_r in self.domains[v_r]:
                        counts[t_l] += 1
            elif variable == v_r:
                for (t_l, t_r) in cs:
                    if t_r in counts and t_l in self.domains[v_l]:
                        counts[t_r] += 1
        return counts
    

    def get_value_order(self, variable: V):
        """
        Heuristic for the order in which values for a variable should be tried.

        Uses the least constraining value heuristic.
        """
        option_counts: dict[T, int] = self.get_option_count_per_assignment(variable)
        return sorted(option_counts, key=lambda t: option_counts[t], reverse=True)
    

    def add_assignment(self, variable: V, value: T) -> bool:
        """
        Adds an assignment to a CSP, running the AC-3 algorithm for constraint propagation.

        Return value indicates whether the CSP is still consistent.
        """
        assert variable in self.variables
        assert variable not in self.assignments
        assert value in self.domains[variable]

        self.assignments[variable] = value
        self.domains[variable] = set((value,))
        return self.ac_3()
    

    def ac_3(self) -> bool:
        """
        AC-3 algorithm for constraint propagation in a CSP.

        Return value indicates whether the CSP is still consistent.
        """
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
        """
        Removes inconsistent domain elements from the origin of a directed constraint.

        Return value denotes whether any domain elements were removed.
        """
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