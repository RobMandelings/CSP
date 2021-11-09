import random
from copy import deepcopy
from typing import Set, Dict, List, TypeVar, Optional
from abc import ABC, abstractmethod

from util import monitor

Value = TypeVar('Value')


class Variable(ABC):
    @property
    @abstractmethod
    def startDomain(self) -> Set[Value]:
        """ Returns the set of initial values of this variable (not taking constraints into account). """
        pass


class CSP(ABC):
    def __init__(self, MRV=True, LCV=True):
        """
        MRV: Minimum Remaining Values (Most constrained variable) -> Used when choosing next unassigned variable
        LCV: Least Constricted Value -> Used when choosing value
        """
        self.MRV = MRV
        self.LCV = LCV

    @property
    @abstractmethod
    def variables(self) -> Set[Variable]:
        """ Return the set of variables in this CSP.
            Abstract method to be implemented for specific instances of CSP problems.
        """
        pass

    def remainingVariables(self, assignment: Dict[Variable, Value]) -> Set[Variable]:
        """ Returns the variables not yet assigned. """
        return self.variables.difference(assignment.keys())

    @abstractmethod
    def neighbors(self, var: Variable) -> Set[Variable]:
        """ Return all variables related to var by some constraint.
            Abstract method to be implemented for specific instances of CSP problems.
        """
        pass

    def assignmentToStr(self, assignment: Dict[Variable, Value]) -> str:
        """ Formats the assignment of variables for this CSP into a string. """
        s = ""
        for var, val in assignment.items():
            s += f"{var} = {val}\n"
        return s

    def isComplete(self, assignment: Dict[Variable, Value]) -> bool:
        """ Return whether the assignment covers all variables.
            :param assignment: dict (Variable -> value)
        """
        # TODO: Implement CSP::isComplete (problem 1)

        if self.isValid(assignment) and len(self.remainingVariables(assignment)) == 0:
            return True

        return False

    @abstractmethod
    def isValidPairwise(self, var1: Variable, val1: Value, var2: Variable, val2: Value) -> bool:
        """ Return whether this pairwise assignment is valid with the constraints of the csp.
            Abstract method to be implemented for specific instances of CSP problems.
        """
        pass

    def isValid(self, assignment: Dict[Variable, Value]) -> bool:
        """ Return whether the assignment is valid (i.e. is not in conflict with any constraints).
            You only need to take binary constraints into account.
            Hint: use `CSP::neighbors` and `CSP::isValidPairwise` to check that all binary constraints are satisfied.
            Note that constraints are symmetrical, so you don't need to check them in both directions.
        """

        assignedVariables = assignment.keys()

        for var in assignedVariables:
            neighbours = self.neighbors(var)

            # Filter out unassigned neighbour variables
            neighbours = [neighbour for neighbour in neighbours if neighbour in assignedVariables]
            # TODO don't check in both directions
            for neighbour in neighbours:
                if not self.isValidPairwise(var, assignment[var], neighbour, assignment[neighbour]):
                    return False

        return True

    def solveBruteForce(self, initialAssignment: Dict[Variable, Value] = dict()) -> Optional[Dict[Variable, Value]]:
        """ Called to solve this CSP with brute force technique.
            Initializes the domains and calls `CSP::_solveBruteForce`. """
        domains = domainsFromAssignment(initialAssignment, self.variables)
        return self._solveBruteForce(initialAssignment, domains)

    # Count the amounts of calls: can be used to answer a question from the assigment
    @monitor
    def _solveBruteForce(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Optional[
        Dict[Variable, Value]]:
        """ Implement the actual backtracking algorithm to brute force this CSP.
            Use `CSP::isComplete`, `CSP::isValid`, `CSP::selectVariable` and `CSP::orderDomain`.
            :return: a complete and valid assignment if one exists, None otherwise.
        """

        # TODO: question, is this function called somewhere else where arc consistency is used for example
        #  (when having to backtrack)
        # TODO: Implement CSP::_solveBruteForce (problem 1)
        # TODO maybe remove duplicate code

        if self.isComplete(assignment):
            return assignment
        else:
            var = self.selectVariable(assignment, domains)

            for value in self.orderDomain(assignment, domains, var):
                assignment[var] = value
                if self.isValid(assignment):
                    result = self._solveBruteForce(deepcopy(assignment), domains)
                    if result is not None:
                        return result
                    assignment.pop(var)

            self.isValid(assignment)
            return None

    def solveForwardChecking(self, initialAssignment: Dict[Variable, Value] = dict()) -> Optional[
        Dict[Variable, Value]]:
        """ Called to solve this CSP with forward checking.
            Initializes the domains and calls `CSP::_solveForwardChecking`. """
        domains = domainsFromAssignment(initialAssignment, self.variables)
        domains, nr_pruned = self.forwardChecking(initialAssignment, domains)
        return self._solveForwardChecking(initialAssignment, domains)

    @monitor
    def _solveForwardChecking(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Optional[
        Dict[Variable, Value]]:
        """ Implement the actual backtracking algorithm with forward checking.
            Use `CSP::forwardChecking` and you should no longer need to check if an assignment is valid.
            :return: a complete and valid assignment if one exists, None otherwise.
        """

        if self.isComplete(assignment):
            return assignment
        else:
            var = self.selectVariable(assignment, domains)

            for value in self.orderDomain(assignment, domains, var):
                assignment[var] = value
                pruned_domains, nr_pruned = self.forwardChecking(assignment, domains, var)

                valid = True
                for pruned_domain in pruned_domains.values():
                    if len(pruned_domain) == 0:
                        valid = False

                if not valid:
                    assignment.pop(var)
                else:
                    result = self._solveForwardChecking(deepcopy(assignment), pruned_domains)

                    if result is not None:
                        return result

            self.isValid(assignment)
            return None

    def forwardChecking(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]],
                        variable: Optional[Variable] = None) -> (Dict[Variable, Set[Value]], Value):

        # Differences noticed: less calls often necessary, although domains still randomly ordered so may take lots of calls.
        # Calls are faster due to checking whether an assignment is valid or not happens faster (pruned)

        """ Implement the forward checking algorithm from the theory lectures.

        :param domains: current domains.
        :param assignment: current assignment.
        :param variable: If not None, the variable that was just assigned (only need to check changes).
        :return: the new domains after enforcing all constraints and the numbers of elements pruned from the domain.
        """

        # Necessary: isValidPairwise -> given current assignment to variable, check domains of all other variables

        domains = deepcopy(domains)
        nr_pruned = 0

        for assigned_var, assigned_value in assignment.items():

            # Filter out already assigned variables
            unassigned_var_domains = {var: domain for var, domain in domains.items() if var not in assignment.keys()}

            for unassigned_var, domain in unassigned_var_domains.items():
                elems_to_remove = set()
                for elem in domain:
                    if not self.isValidPairwise(assigned_var, assigned_value, unassigned_var, elem):
                        elems_to_remove.add(elem)
                        nr_pruned += 1

                domains[unassigned_var] = domain.difference(elems_to_remove)

                if len(domain) == 0:
                    return domains, nr_pruned

        return domains, nr_pruned

    def selectVariable(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Variable:
        """ Implement a strategy to select the next variable to assign. """
        if not self.MRV:
            return random.choice(list(self.remainingVariables(assignment)))

        unassigned_var_domains = {var: domain for var, domain in domains.items() if var not in assignment.keys()}
        domain_lengths = {var: len(domain) for var, domain in unassigned_var_domains.items()}
        min_domain_length = min(domain_lengths.values())

        for current_var, current_domain_length in domain_lengths.items():
            if current_domain_length == min_domain_length:
                return current_var

    def orderDomain(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]], var: Variable) -> \
            List[Value]:
        """ Implement a smart ordering of the domain values. """
        if not self.LCV:
            return list(domains[var])

        unassigned_var_domains = {var: domain for var, domain in domains.items() if var not in assignment.keys()}
        domain_to_order = domains[var]

        value_nr_pruned_dict = dict()

        for val in domain_to_order:
            current_assignment = deepcopy(assignment)
            current_assignment[var] = val

            pruned_domains, nr_pruned = self.forwardChecking(current_assignment, unassigned_var_domains)

            # LCV only works properly if the pruned domains do not contain empty sets
            contains_empty_domain = False
            for pruned_var, pruned_domain in pruned_domains.items():
                if len(pruned_domain) == 0:
                    contains_empty_domain = True

            if not contains_empty_domain:
                value_nr_pruned_dict[val] = nr_pruned

        ordered_value_nr_pruned_dict = dict(
            sorted(value_nr_pruned_dict.items(), key=lambda item: item[1], reverse=False))
        ordered_domain = list(ordered_value_nr_pruned_dict.keys())

        return ordered_domain

    def solveAC3(self, initialAssignment: Dict[Variable, Value] = dict()) -> Optional[Dict[Variable, Value]]:
        """ Called to solve this CSP with AC3.
            Initializes domains and calls `CSP::_solveAC3`. """
        domains = domainsFromAssignment(initialAssignment, self.variables)
        domains = self.ac3(initialAssignment, domains)
        return self._solveAC3(initialAssignment, domains)

    @monitor
    def _solveAC3(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Optional[
        Dict[Variable, Value]]:
        """
            Implement the actual backtracking algorithm with AC3.
            Use `CSP::ac3`.
            :return: a complete and valid assignment if one exists, None otherwise.
        """
        # TODO: Implement CSP::_solveAC3 (problem 3)
        pass

    def ac3(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]],
            variable: Optional[Variable] = None) -> Dict[Variable, Set[Value]]:
        """ Implement the AC3 algorithm from the theory lectures.

        :param domains: current domains.
        :param assignment: current assignment.
        :param variable: If not None, the variable that was just assigned (only need to check changes).
        :return: the new domains ensuring arc consistency.
        """
        # TODO: Implement CSP::ac3 (problem 3)
        pass


def domainsFromAssignment(assignment: Dict[Variable, Value], variables: Set[Variable]) -> Dict[Variable, Set[Value]]:
    """ Fills in the initial domains for each variable.
        Already assigned variables only contain the given value in their domain.
    """
    domains = {v: v.startDomain for v in variables}
    for var, val in assignment.items():
        domains[var] = {val}
    return domains
