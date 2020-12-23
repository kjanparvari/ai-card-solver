import time


class Card:
    _number: int
    _color: str

    def __init__(self, card_id: str):
        number: str = ""
        color: str = ""
        for i in range(0, len(card_id)):
            if card_id[i].isdigit():
                number += card_id[i]
            else:
                color = card_id[i:len(card_id)]
                break
        self._color = color
        self._number = int(number)

    def getColor(self) -> str:
        return self._color

    def getNumber(self) -> int:
        return self._number

    def getId(self) -> str:
        return str(self._number) + self._color

    def __str__(self) -> str:
        return self.getId()


class Section:
    _cards: [Card]
    _number: int
    _cards_number: int

    def __init__(self, number: int, cards_number: int):
        self._number = number
        self._cards = []
        self._cards_number = cards_number

    def getNumber(self) -> int:
        return self._number

    def getCard(self, index=None) -> Card or None:
        length: int = len(self._cards)
        if index is None:
            index = length - 1
        if length > 0 and index < length:
            return self._cards[index]
        return None

    def popCard(self, index=None) -> Card or None:
        length: int = len(self._cards)
        if index is None:
            index = length - 1
        if length > 0 and index < length:
            return self._cards.pop(index)
        return None

    def addCard(self, card: Card) -> None:
        self._cards.append(card)

    def isGoal(self) -> bool:
        list_length: int = len(self._cards)
        if list_length == 0:
            return True
        if list_length != self._cards_number:
            return False
        color = self._cards[0].getColor()
        for i in range(0, list_length - 1):
            current_card: Card = self._cards[i]
            next_card: Card = self._cards[i + 1]
            if (current_card.getNumber() < next_card.getNumber()) or (next_card.getColor() != color):
                return False
        return True

    def __str__(self) -> str:
        s: str = ""
        for c in self._cards:
            s += str(c) + " "
        return s if s != "" else "#"


class Board:
    _sections: {Section}

    def __init__(self):
        self._sections = {}

    def addSection(self, section: Section) -> None:
        self._sections[section.getNumber()] = section

    def _moveCard(self, src: int, dst: int):
        card = self._sections[src].popCard()
        if card is not None:
            self._sections[dst].addCard(card)

    def _moveIsValid(self, src: int, dst: int) -> bool:
        src_card = self._sections[src].getCard()
        dst_card = self._sections[dst].getCard()
        if (src_card is None) or src == dst:
            return False
        elif dst_card is None:
            return True
        else:
            return True if dst_card.getNumber() > src_card.getNumber() else False

    def getValidMoves(self, moves: [(int, int)]) -> [(int, int)]:
        for (src, dst) in moves:
            self._moveCard(src, dst)
        result: [(int, int)] = []
        length: int = len(self._sections)
        for i in range(0, length):
            for j in range(0, length):
                if self._moveIsValid(i, j):
                    result.append((i, j))
        for (src, dst) in reversed(moves):
            self._moveCard(dst, src)
        return result

    def checkMoves(self, moves: [(int, int)]) -> (bool, str):
        result: (bool, str)
        for (src, dst) in moves:
            self._moveCard(src, dst)
        result = (self.isGoal(), str(self))
        for (src, dst) in reversed(moves):
            self._moveCard(dst, src)
        return result

    def isGoal(self, moves: [(int, int)] or None = None) -> bool:
        if moves is None:
            moves = []
        for (src, dst) in moves:
            self._moveCard(src, dst)
        section: Section
        result: bool = True
        for i in range(0, len(self._sections)):
            if not self._sections[i].isGoal():
                result = False
                break
        for (src, dst) in reversed(moves):
            self._moveCard(dst, src)
        return result

    def __str__(self) -> str:
        s: str = ""
        for i in range(0, len(self._sections)):
            s += str(self._sections[i]) + "\n"
        return s

    def print(self) -> None:
        print(self)


class Node:
    _path: [(int, int)]  # list of movements (src, dst)
    _state: str

    def __init__(self, path: [(int, int)], state=""):
        self._path = path
        self._state = state

    def getDepth(self) -> int:
        return len(self._path)

    def setState(self, state: str) -> None:
        self._state = state

    def getState(self) -> str:
        return self._state

    def getPath(self) -> [(int, int)]:
        return self._path

    def __str__(self) -> str:
        s: str = str(self.getDepth()) + "\n"
        src: int
        dst: int
        for (src, dst) in self._path:
            s += str(src + 1) + " -> " + str(dst + 1) + "\n"
        return s


class Tree:
    _board: Board
    _expand_counter: int
    _generate_counter: int
    _start_time: time

    def __init__(self, board: Board):
        self._board = board
        self._expand_counter = 0
        self._generate_counter = 0

    def printDetails(self):
        print("number of expanded nodes: ", self._expand_counter)
        print("number of generated nodes: ", self._generate_counter)
        print("time: ", int(time.time() - self._start_time), " seconds")

    def ids(self, limit: int) -> Node or str:
        self._start_time = time.time()
        result: Node or str = "failure"
        depth: int
        for depth in range(0, limit + 1):
            # print("depth: ", depth)
            result = self.dls(depth)
            if result != "cuttoff":
                return result

    def dls(self, limit: int) -> Node or str:
        init_node = Node([], str(self._board))
        return self._recursive_dls(init_node, limit)

    def _recursive_dls(self, node: Node, limit: int) -> Node or str:
        if self._board.isGoal(node.getPath()):
            return node
        elif limit == 0:
            return "cuttoff"
        else:
            cuttoff_occurred = False
            moves: [(int, int)] = self._board.getValidMoves(node.getPath())
            self._expand_counter += 1
            for move in moves:
                new_path: [(int, int)] = node.getPath() + [move]
                child: Node = Node(new_path)
                self._generate_counter += 1
                result = self._recursive_dls(child, limit - 1)
                if result == "cuttoff":
                    cuttoff_occurred = True
                elif result != "failure":
                    return result
            if cuttoff_occurred:
                return "cuttoff"
            else:
                return "failure"


def main():
    [k, m, n] = list(map(int, input().split()))
    board = Board()
    for i in range(0, k):
        section = Section(i, n)
        cards_raw = input()
        if cards_raw != "#":
            for c in cards_raw.split(" "):
                section.addCard(Card(c))
        board.addSection(section)
    tree = Tree(board)
    solution = tree.ids(8)
    print(solution) if solution is not None else print("Failure")
    tree.printDetails()


if __name__ == '__main__':
    main()
