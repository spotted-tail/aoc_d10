import sys
import argparse
from collections import namedtuple

PipeExit = namedtuple('PipeExit', 'direction, coord')

class Coord():
    def __init__(self, row, column):
        self._row = row
        self._column = column
    
    @property 
    def row(self):
        return self._row
    
    @row.setter
    def row(self, row):
        self._row = row

    @property 
    def column(self):
        return self._column
    
    @column.setter
    def column(self, column):
        self._column = column


class Map():
    def __init__(self):
        self._map = None
        self._columns = 0
        self._rows = 0

    def read_map(self, filename):
        self._map = []
        column = 0
        row = 0
        try:
            with open(filename, 'r') as fptr:
                for line in fptr:
                    print(line, end='')
                    map_row = []
                    column = 0
                    for map_char in list(line.rstrip()):
                        point = Coord(row, column)
                        map_row.append(Pipe(map_char, point))
                        column += 1
                    self._map.append(map_row)
                    row += 1

        except IOError:
            print(f"Error: Could not open \'{filename}\'")
            sys.exit(0)

        self._rows = len(self._map[0])
        self._columns = len(self._map)

    def print_map(self):
        for row in range(self._rows):
            for column in range(self._rows):
                print(f'{self._map[row][column].symbol}', end='')
            print()

    def find_start_coord(self):
        for row in range(self._rows):
            for column in range(self._rows):
                if self._map[row][column].symbol == 'S':
                    return self._map[row][column].coord

        return None

    def get_pipe(self, row, column):
        if (0 <= column <= self._columns) and (0 <= row <= self._rows):
            return self._map[row][column]
        else:
            return None

    def find_creature(self):
        start_coord = self.find_start_coord()
        if start_coord: 
            print(f'{start_coord.row}, {start_coord.column}')
        else:
            print('ERROR: Could not find start coord. Invalid Map')
            sys.exit(0)

        exit_count = self.count_neighbor_exits(start_coord)
        if exit_count < 2:
            print('ERROR: Invalid Map')
            sys.exit(0)
        if exit_count > 2:
            print('ERROR: Nominally Invalid Map. Could have dead ends next to start pipe')
            sys.exit(0)

        self.identify_loop(start_coord)

    def count_neighbor_exits(start_coord):
        count = 0
        directions = ['n','e', 'w', 's']
        for direction in directions:
            if self.check_neighbor_exit(direction, start_coord):
                count += count
        return count
    
    def check_neighbor_exit(self, start_point):
        offsets = [('n', [-1, 0]),
                   ('e', [0, 1]),
                   ('s', [1, 0]),
                   ('w', [0, -1])]

        opp_dir= [('n', 's'),
                  ('e', 'w'),
                  ('s', 'n'),
                  ('w', 'e')]

        for direction in offsets:
            offset = offsets[direction]
            pipe = self.get_pipe(start_point.row + offset[0],
                                 start_point.column + offset[1])
            if pipe and pipe.has_exit(opp_dir[direction]):
                return True

        return False
    
    def find_exit(self, start_point):
        #check_north
        pipe = self.get_pipe(start_point[0] - 1, start_point[1])
        if pipe and pipe.has_south_exit():
            return PipeExit('n', start_point[0] - 1, start_point[1])

        #check_east
        pipe = self.get_pipe(start_point[0], start_point[1] + 1)
        if pipe and pipe.has_west_exit():
            return PipeExit('e', start_point[0], start_point[1] + 1)

        #check_south
        pipe = self.get_pipe(start_point[0] + 1, start_point[1])
        if pipe and pipe.has_north_exit():
            return PipeExit('s', start_point[0] + 1, start_point[1])

        #check_west
        pipe = self.get_pipe(start_point[0], start_point[1] - 1)
        if pipe and pipe.has_east_exit():
            return PipeExit('w', start_point[0], start_point[1] - 1)

        return None
    
    def identify_loop(self, start_point):
        first_exit = self.find_exit(start_point)
        if first_exit:
            print(f'{first_exit.direction}', {first_exit.y}, {first_exit.x})
            

class Pipe:
    def __init__(self, symbol, coord):
        symbols = ['.', 'F', '-', '7', '|', 'L', 'J', 'S']
        if symbol in symbols:
            self.symbol = symbol
        else:
            print(f"ERROR: Symbol \'{symbol}\' not legal")
            print(f'Expecting one of {symbols}')
            sys.exit(0)

        self.coord = coord

    @property
    def symbol(self):
        return self._symbol
    
    @symbol.setter
    def symbol(self, symbol):
        self._symbol = symbol

    @property
    def coord(self):
        return self._coord
    
    @coord.setter
    def coord(self, coord):
        self._coord = coord

    def has_exit(self, direction):
        exits = [('n', ['|', 'L', 'J']),
                 ('e', ['F','-','L']),
                 ('s', ['F', '7', '|']),
                 ('w', ['-', '7', 'J'])]

        if self.symbol in exits[direction]:
            return True
        else:
            return False


def parse_commandline():
    # Instantiate the parser
    parser = argparse.ArgumentParser(description='Optional app description')

    # Required positional argument
    parser.add_argument('-m', '--map', type=str,
                        help='Filename for a pipe map')

    return parser.parse_args()


def main():
    args = parse_commandline()
    map = Map()
    map.read_map(args.map)
    map.print_map()
    #map.find_creature()

if __name__ == '__main__':
    main()