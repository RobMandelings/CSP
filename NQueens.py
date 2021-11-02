from typing import Set, Dict

from CSP import CSP, Variable, Value


class NQueens(CSP):
    def __init__(self, n=4, MRV=True, LCV=True):
        super().__init__(MRV=MRV, LCV=LCV)
        self.n = n
        self._variables = set(Queen(col, self.n) for col in range(self.n))

    @property
    def variables(self) -> Set['Queen']:
        """ Return the set of variables in this CSP. """
        return self._variables

    def neighbors(self, var: 'Queen') -> Set['Queen']:
        """ Return all variables related to var by some constraint. """
        return self.variables - {var}

    def isValidPairwise(self, var1: 'Queen', val1: Value, var2: 'Queen', val2: Value) -> bool:
        """ Return whether this pairwise assignment is valid with the constraints of the csp. """
        col1, row1 = var1.col, val1
        col2, row2 = var2.col, val2

        if row1 == row2:                                # same row
            return False

        if abs(row1 - row2) == abs(col1 - col2):        # diagonal
            return False

        return True

    def assignmentToStr(self, assignment: Dict['Queen', Value]) -> str:
        """ Formats the assignment of variables for this CSP into a string. """
        if len(assignment) > 80:
            return super().assignmentToStr(assignment)
        border = "+" + "-" * (self.n) + "+"
        s = border + "\n"
        SPACE = " "
        row_to_col_map = {row: var.col for var, row in assignment.items()}
        for row in range(self.n):
            if row in row_to_col_map:
                col = row_to_col_map[row]
                s += "|" + SPACE * col + "Q" + SPACE * (self.n - col - 1) + "|\n"
            else:
                s += "|" + SPACE * self.n + "|\n"
        s += border

        return s


class Queen(Variable):
    def __init__(self, col, boardsize):
        self.col = col
        self.boardsize = boardsize

    def __repr__(self):
        return f"Q{self.col}"

    def __eq__(self, other):
        return isinstance(other, Queen) and self.col == other.col and self.boardsize == other.boardsize

    def __hash__(self):
        return hash((self.col, self.boardsize))

    def __copy__(self):
        return self

    def __deepcopy__(self, memodict={}):
        return self

    @property
    def startDomain(self) -> Set[Value]:
        return set(range(self.boardsize))
