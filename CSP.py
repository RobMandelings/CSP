import random
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
        # TODO: Implement CSP::isValid (problem 1)
        pass

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

        if self.isComplete(assignment):
            return assignment
        else:
            var = self.selectVariable(assignment, domains)

            for value in self.orderDomain(assignment, domains, var):
                assignment[var] = value
                if self.isValid(assignment):
                    result = self._solveBruteForce(assignment, domains)
                    if result is not None:
                        return result
                    assignment.pop(var)

            return None

    def solveForwardChecking(self, initialAssignment: Dict[Variable, Value] = dict()) -> Optional[
        Dict[Variable, Value]]:
        """ Called to solve this CSP with forward checking.
            Initializes the domains and calls `CSP::_solveForwardChecking`. """
        domains = domainsFromAssignment(initialAssignment, self.variables)
        domains = self.forwardChecking(initialAssignment, domains)
        return self._solveForwardChecking(initialAssignment, domains)

    @monitor
    def _solveForwardChecking(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Optional[
        Dict[Variable, Value]]:
        """ Implement the actual backtracking algorithm with forward checking.
            Use `CSP::forwardChecking` and you should no longer need to check if an assignment is valid.
            :return: a complete and valid assignment if one exists, None otherwise.
        """
        # TODO: Implement CSP::_solveForwardChecking (problem 2)
        pass

    def forwardChecking(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]],
                        variable: Optional[Variable] = None) -> Dict[Variable, Set[Value]]:
        """ Implement the forward checking algorithm from the theory lectures.

        :param domains: current domains.
        :param assignment: current assignment.
        :param variable: If not None, the variable that was just assigned (only need to check changes).
        :return: the new domains after enforcing all constraints.
        """
        # TODO: Implement CSP::forwardChecking (problem 2)
        pass

    def selectVariable(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Variable:
        """ Implement a strategy to select the next variable to assign. """
        if not self.MRV:
            return random.choice(list(self.remainingVariables(assignment)))

        # TODO: Implement CSP::selectVariable (problem 2)

    def orderDomain(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]], var: Variable) -> \
            List[Value]:
        """ Implement a smart ordering of the domain values. """
        if not self.LCV:
            return list(domains[var])

        # TODO: Implement CSP::orderDomain (problem 2)

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
