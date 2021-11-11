from math import ceil, floor

from typing import Set, Dict

from CSP import CSP, Variable, Value

class Sudoku(CSP):
    def __init__(self, MRV=True, LCV=True):
        super().__init__(MRV=MRV, LCV=LCV)

        self._variables = set()

        for row in range(0, 9):
            for column in range(0, 9):
                self._variables.add(Cell(row, column))

        print('hi')

    @property
    def variables(self) -> Set['Cell']:
        """ Return the set of variables in this CSP. """
        return self._variables

    def getCell(self, x: int, y: int) -> 'Cell':
        """ Get the  variable corresponding to the cell on (x, y) """
        for variable in self.variables:
            if variable.row == y and variable.column == x:
                return variable
        raise AssertionError(f"Could not get cell at position ({x}, {y})")

    def neighbors(self, var: 'Cell') -> Set['Cell']:
        """ Return all variables related to var by some constraint. """

        # All variables in the same cell, all variables in the same row and all variables in the same column
        neighbours = set()

        for current_var in self.variables:
            if current_var == var:
                continue

            if current_var.row == var.row:
                neighbours.add(current_var)
            elif current_var.column == var.column:
                neighbours.add(current_var)
            elif current_var.squarePos == var.squarePos:
                neighbours.add(current_var)

        return neighbours

    def isValidPairwise(self, var1: 'Cell', val1: Value, var2: 'Cell', val2: Value) -> bool:
        """ Return whether this pairwise assignment is valid with the constraints of the csp. """

        if val1 == val2:
            if var1.row == var2.row:
                return False
            elif var1.column == var2.column:
                return False
            elif var1.squarePos == var2.squarePos:
                return False

        return True

    def assignmentToStr(self, assignment: Dict['Cell', Value]) -> str:
        """ Formats the assignment of variables for this CSP into a string. """
        s = ""
        for y in range(9):
            if y != 0 and y % 3 == 0:
                s += "---+---+---\n"
            for x in range(9):
                if x != 0 and x % 3 == 0:
                    s += '|'

                cell = self.getCell(x, y)
                s += str(assignment.get(cell, ' '))
            s += "\n"
        return s

    def parseAssignment(self, path: str) -> Dict['Cell', Value]:
        """ Gives an initial assignment for a Sudoku board from file. """
        initialAssignment = dict()

        with open(path, "r") as file:
            for y, line in enumerate(file.readlines()):
                if line.isspace():
                    continue
                assert y < 9, "Too many rows in sudoku"

                for x, char in enumerate(line):
                    if char.isspace():
                        continue

                    assert x < 9, "Too many columns in sudoku"

                    var = self.getCell(x, y)
                    val = int(char)

                    if val == 0:
                        continue

                    assert val > 0 and val < 10, f"Impossible value in grid"
                    initialAssignment[var] = val
        return initialAssignment

class Cell(Variable):
    def __init__(self, row, column):
        super().__init__()
        self._row = row
        self._column = column

    def __repr__(self):
        return f"C[{self.row}, {self.column}]"

    def __hash__(self):
        return hash((self.row, self.column))

    def __eq__(self, other: 'Cell'):
        return self.row == other.row and self.column == other.column

    @property
    def row(self) -> int:
        return self._row

    @property
    def column(self) -> int:
        return self._column

    @property
    def squarePos(self) -> (int, int):
        """
        Returns tuple (row, column) telling in which 3x3 square the cell is located
        """
        return floor(self.row / 3.0), floor(self.column / 3.0)

    @property
    def startDomain(self) -> Set[Value]:
        """ Returns the set of initial values of this variable (not taking constraints into account). """
        return {val for val in range(1, 10)}
