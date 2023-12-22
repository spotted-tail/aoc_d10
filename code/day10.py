import sys
import argparse


def get_tile_offset(direction):
    keys = ['n', 'e', 's', 'w']
    values = [Coord(-1, 0), Coord(0, 1), Coord(1, 0), Coord(0, -1)]
    offsets = dict(zip(keys, values))
    if direction in offsets:
        return offsets[direction]
    else:
        return None


def get_mirror_direction(direction):
    keys = ['n', 'e', 's', 'w']
    values = ['s', 'w', 'n', 'e']
    opp_dir = dict(zip(keys, values))
    if direction in opp_dir:
        return opp_dir[direction]
    else:
        return None
    
def get_other_exit(symbol, direction):
    keys = ['n', 'e', 's', 'w']
    values = [['|', 'L', 'J'], ['F','-','L'], ['F', '7', '|'], ['-', '7', 'J']]

    exits = {}

    exits['|'] = {}
    exits['|']['n'] = 'n'
    exits['|']['s'] = 's'

    exits['-'] = {}
    exits['-']['e'] = 'e'
    exits['-']['w'] = 'w'

    exits['L'] = {}
    exits['L']['s'] = 'e'
    exits['L']['w'] = 'n'

    exits['J'] = {}
    exits['J']['s'] = 'w'
    exits['J']['e'] = 'n'

    exits['7'] = {}
    exits['7']['n'] = 'w'
    exits['7']['e'] = 's'

    exits['F'] = {}
    exits['F']['n'] = 'e'
    exits['F']['w'] = 's'

    if symbol in exits:
        if direction in exits[symbol]:
            return exits[symbol][direction]
        else: 
            return None
    else:
        return None
    

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

    def __add__(self, coord):
        return Coord(self.row + coord.row, self.column + coord.column)

    def __str__(self):
        return f'({self.row}, {self.column})'

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
        #self.connect_pipes()

    def print_map(self):
        print('Input Map:')
        for row in range(self._rows):
            for column in range(self._rows):
                print(f'{self._map[row][column].symbol}', end='')
            print('')
        print('')

    def find_start_coord(self):
        for row in range(self._rows):
            for column in range(self._rows):
                if self._map[row][column].symbol == 'S':
                    return self._map[row][column].coord
        return None

    def get_pipe(self, coord):
        if (0 <= coord.column <= self._columns) and (0 <= coord.row <= self._rows):
            return self._map[coord.row][coord.column]
        else:
            return None

    def find_creature(self, debug):
        start_coord = self.find_start_coord()
        if not start_coord: 
            print('ERROR: Could not find start coord. Invalid Map')
            sys.exit(0)

        exit_count = self.count_neighbor_exits(start_coord)
        if exit_count < 2:
            print(f'ERROR: Invalid Map. Start point has {exit_count} exit(s)')
            sys.exit(0)
        if exit_count > 2:
            print('ERROR: Nominally Invalid Map. Could have dead ends next to start pipe')
            sys.exit(0)

        self.identify_loop(start_coord, debug)

    def count_neighbor_exits(self, start_coord):
        count = 0
        directions = ['n','e', 'w', 's']
        for direction in directions:
            if self.check_neighbor_exit(direction, start_coord):
                count += 1
        return count
    
    def check_neighbor_exit(self, direction, start_point):
        tile_coord = start_point + get_tile_offset(direction)
        pipe = self.get_pipe(tile_coord)
        if pipe and pipe.has_exit(get_mirror_direction(direction)):
            return True

        return False
    
    def find_exit(self, start_point):
        directions = ['n','e', 's', 'w']
        for direction in directions:
            tile_coord = start_point + get_tile_offset(direction)
            pipe = self.get_pipe(tile_coord)
            if pipe and pipe.has_exit(get_mirror_direction(direction)):
                return direction
        return None
    
    def identify_loop(self, start_point, debug=0):
        print(f'Starting position = {start_point}')
        direction = self.find_exit(start_point)
        if direction:
            path = self.crawl(direction, start_point)

        creature_distance = int(len(path)/2)
        print(f'Creature is {creature_distance} positions away from starting position.')
        print(f'Creature can be found at {path[creature_distance].coord}')

        if debug:
            print("Pathing:")
            count = 1
            for pipe in path:
                if count == creature_distance:
                    print("*", end='')
                print(f'{pipe.symbol} @{pipe.coord}')
                count += 1
        

    def crawl(self, starting_direction, coord):
        done = False
        path = []
        pipe = self.get_pipe(coord)
        direction = starting_direction
        while not done: 
            new_coord = pipe.coord + get_tile_offset(direction)
            pipe = self.get_pipe(new_coord)
            #print(f'went {direction} to {new_coord} and found {pipe.symbol}')
            direction = get_other_exit(pipe.symbol, direction)
            path.append(pipe)
            if pipe.symbol == 'S':
                done = True
        return path


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
        keys = ['n', 'e', 's', 'w']
        values = [['|', 'L', 'J'], ['F','-','L'], ['F', '7', '|'], ['-', '7', 'J']]
        exits = dict(zip(keys, values))
        if self.symbol in exits[direction]:
            return True
        else:
            return False
        
    def __str__(self):
        return f'{self.symbol} @{self.coord}'


def parse_commandline():
    # Instantiate the parser
    parser = argparse.ArgumentParser(description='Optional app description')

    parser.add_argument('-m', '--map', type=str,
                        help='Filename for a pipe map')

    parser.add_argument('-d', '--debug', 
                        action="store_true",
                        help='Filename for a pipe map')
    
    return parser.parse_args()

def debug_tile_offsets():
    coord = Coord(1,3)
    print(coord)
    for dir in ['n', 'e', 's', 'w']:
        offset = get_tile_offset(dir)

        print(f'Tile coord in the {dir} direction is {coord + offset}')

    
def main():
    map = Map()
    args = parse_commandline()
    map.read_map(args.map)
    map.print_map()
    map.find_creature(args.debug)

if __name__ == '__main__':
    main()