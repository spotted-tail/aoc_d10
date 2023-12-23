import sys
import math
import argparse


def get_tile_offset(direction):
    keys = ['n', 'e', 's', 'w']
    values = [Coord(-1, 0), Coord(0, 1), Coord(1, 0), Coord(0, -1)]
    offsets = dict(zip(keys, values))
    if direction in offsets:
        return offsets[direction]
    else:
        return None


def get_direction(direction, angle):
    directions = ['n', 'e', 's', 'w']

    if direction in directions:
        index = (int((angle/90) % 90) + directions.index(direction)) % 4
        return directions[index]
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

    def __eq__(self, other):
        if (self.row == other.row) and (self.column == other.column):
            return True
        else:
            return False


class Map():
    def __init__(self):
        self._map = None
        self._columns = 0
        self._rows = 0
        self._path = []

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
                        map_row.append(Tile(map_char, point))
                        column += 1
                    self._map.append(map_row)
                    row += 1
        except IOError:
            print(f"Error: Could not open \'{filename}\'")
            sys.exit(0)

        self._columns = len(self._map[0])
        self._rows = len(self._map)

    def print_input_map(self):
        print('Input Map:')
        for row in range(self._rows):
            for column in range(self._columns):
                print(f'{self._map[row][column].symbol}', end='')
            print('')
        print('')

    def print_cavity_map(self):
        print('Cavity Map:')
        for row in range(self._rows):
            for column in range(self._columns):
                tile = self._map[row][column]
                char = tile.symbol
                if not tile.is_loop:
                    if self._map[row][column].is_inside:
                        char = "I"
                    else:
                        if tile.is_ground:
                            char = "O"
                print(f'{char}', end='')
            print('')
        print('')

    def get_tile(self, coord):
        if (0 <= coord.column < self._columns) and (0 <= coord.row < self._rows):
            return self._map[coord.row][coord.column]
        else:
            return None

    def find_start_coord(self):
        for row in range(self._rows):
            for column in range(self._columns):
                if self._map[row][column].symbol == 'S':
                    return self._map[row][column].coord
        return None

    def get_neighbor_signature(self, start_coord):
        code = 0
        count = 0
        directions = ['n','e', 's', 'w']
        for direction in directions:
            if self.check_neighbor_exit(direction, start_coord):
                code += 2**count
            count += 1
        return code
    
    def check_neighbor_exit(self, direction, start_coord):
        tile_coord = start_coord + get_tile_offset(direction)
        tile = self.get_tile(tile_coord)
        if tile and tile.has_exit(get_direction(direction, 180)):
            return True

        return False
    
    def find_exit(self, start_coord):
        directions = ['n','e', 's', 'w']
        for direction in directions:
            tile_coord = start_coord + get_tile_offset(direction)
            tile = self.get_tile(tile_coord)
            if tile and tile.has_exit(get_direction(direction, 180)):
                return direction
        return None
    
    def extract_loop(self, debug):
        start_point_alias = {}
        start_point_alias[3] = 'L'
        start_point_alias[5] = '|'
        start_point_alias[6] = 'F'
        start_point_alias[9] = 'J'
        start_point_alias[10] = '-'
        start_point_alias[12] = '7'

        start_coord = self.find_start_coord()
        if not start_coord: 
            print('ERROR: Could not find start coord. Invalid Map')
            sys.exit(0)

        exit_signature = self.get_neighbor_signature(start_coord)
        if not exit_signature or not math.log(exit_signature, 2).is_integer:
            print(f'ERROR: Invalid Map. Start point does not have enough exits.')
            sys.exit(0)
        if exit_signature not in start_point_alias:
            print('ERROR: Nominally Invalid Map. Could have dead ends next to start tile')
            sys.exit(0)
        start_tile = self.get_tile(start_coord)
        start_tile.alias = start_point_alias[exit_signature]
        direction = self.find_exit(start_coord)
        if direction:
            path = self.crawl(direction, start_coord)

        self._path = path    

    def crawl(self, starting_direction, coord):
        done = False
        path = []
        tile = self.get_tile(coord)
        tile.is_loop = True
        direction = starting_direction
        while not done: 
            new_coord = tile.coord + get_tile_offset(direction)
            tile = self.get_tile(new_coord)
            tile.is_loop = True
            #print(f'went {direction} to {new_coord} and found {tile.symbol}')
            direction = get_other_exit(tile.symbol, direction)
            path.append(tile)
            if tile.symbol == 'S':
                done = True
        return path

    def find_highest_corner(self):
        for row in range(self._rows):
            for column in range(self._columns):
                tile = self._map[row][column]
                if tile.alias == 'F' and tile.is_loop:
                    return tile

    def tag_tiles_on_rhs(self, tile, direction):
        rhs = get_direction(direction, 90)
        offset = get_tile_offset(rhs)
        done = False
        coord = tile.coord + offset
        while not done:
            tile = self.get_tile(coord)
            if tile:
                if tile.is_loop:
                    done = True
                else:
                    tile.is_inside = True
                coord = tile.coord + offset
            else: 
                done = True

    def classify_tiles(self):
        highest_corner = self.find_highest_corner()
        tile = highest_corner
        done = False
        direction = 'e'
        print(f'Higest Corner: {tile}')
        count = 0
        while not done: 
            new_coord = tile.coord + get_tile_offset(direction)
            tile = self.get_tile(new_coord)
            self.tag_tiles_on_rhs(tile, direction)
            count += 1
            #print(f'Step {count} Checking from {tile} in {direction} direction')
            direction = get_other_exit(tile.alias, direction)
            if tile.is_corner:
                self.tag_tiles_on_rhs(tile, direction)
              
            if tile.coord == highest_corner.coord:
                done = True

    def print_tile_count_summary(self):
        tile_counts = {}
        location_counts = {}
        loop_tile_count = 0
        symbols = ['.', 'F', '-', '7', '|', 'L', 'J', 'S']
        for symbol in symbols:
            tile_counts[symbol] = 0
        
        locations = ['O', 'I']
        for location in locations:
            location_counts[location] = 0

        for row in range(self._rows):
            for column in range(self._columns):
                tile = self._map[row][column]
                if tile.is_loop:
                    loop_tile_count += 1
                else:
                    if tile.is_inside:
                        location_counts['I'] += 1
                    else:
                        location_counts['O'] += 1
                tile_counts[tile.symbol] += 1

        print (f'Map is {self._rows}x{self._columns}. There are {self._rows * self._columns} total tiles.')
        print('Tile Counts:')
        count = 0
        for symbol in tile_counts:
            print(f'{symbol}:{tile_counts[symbol]}')
            count += tile_counts[symbol]
        print (f'Total Tile Count: {count}')
        print (f'Total Loop Tiles: {loop_tile_count}')

        print('Location Counts:')
        for location in location_counts:
            print(f'{location}:{location_counts[location]}')

class Tile:
    def __init__(self, symbol, coord):
        symbols = ['.', 'F', '-', '7', '|', 'L', 'J', 'S']
        if symbol in symbols:
            self.symbol = symbol
            self.alias = symbol
        else:
            print(f"ERROR: Symbol \'{symbol}\' not legal")
            print(f'Expecting one of {symbols}')
            sys.exit(0)

        self.coord = coord
        self.is_loop = False
        self.is_inside = False

    @property
    def is_corner(self):
        if self.alias in ['F', '7', 'L', 'J']:
            return True
        return False

    @property
    def is_ground(self):
        if self.alias in ['.']:
            return True
        return False

    @property
    def is_inside(self):
        return self._is_inside
    
    @is_inside.setter
    def is_inside(self, is_inside):
        self._is_inside = is_inside

    @property
    def is_loop(self):
        return self._is_loop
    
    @is_loop.setter
    def is_loop(self, is_loop):
        self._is_loop = is_loop

    @property
    def symbol(self):
        return self._symbol
    
    @symbol.setter
    def symbol(self, symbol):
        self._symbol = symbol

    @property
    def alias(self):
        if self.symbol == 'S':
            return self._alias
        else:
            return self.symbol
    
    @alias.setter
    def alias(self, alias):
        self._alias = alias

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
        if self.alias in exits[direction]:
            return True
        else:
            return False
        
    def __str__(self):
        return f'{self.symbol} aka {self.alias} @{self.coord} '\
               f'is_loop {self.is_loop} '\
               f'is_inside {self.is_inside} '


def parse_commandline():
    # Instantiate the parser
    parser = argparse.ArgumentParser(description='Optional app description')

    parser.add_argument('-m', '--map', type=str,
                        help='Filename for a tile map')

    parser.add_argument('-d', '--debug', 
                        action="store_true",
                        help='Filename for a tile map')
    
    return parser.parse_args()


def main():
    map = Map()
    args = parse_commandline()
    map.read_map(args.map)
    map.print_input_map()
    map.extract_loop(args.debug)
    map.classify_tiles()
    map.print_cavity_map()
    map.print_tile_count_summary()
    

if __name__ == '__main__':
    main()