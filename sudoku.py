from random import sample
import curses
import random
import os
import time

RESA = '\033[0m' #RESET_ALL
OKGREEN = '\033[92m'
FAIL = '\033[91m'
red = '\033[31m'
orange = '\033[33m'
lightcyan = '\033[96m'
OKBLUE = '\033[94m'

base = 3
side = base*base
difficulty = "NONE"


def difficulty_set():
    os.system("cls")
    print(f"{lightcyan}> {RESA}Press '{FAIL}Q{RESA}' to quit at anytime!")
    print(f"{lightcyan}> {RESA}Press '{OKBLUE}E{RESA}' to check if the solution is correct!")
    difficulty = input(f"{lightcyan}> {RESA}Choose difficulty ({OKGREEN}easy{RESA}, {orange}medium{RESA}, {FAIL}hard{RESA}): ")
    
    if difficulty == "easy":
        num_cells = random.randint(41, 45) #36 to 40 clues
    elif difficulty == "medium":
        num_cells = random.randint(48, 54) #27 to 33 clues
    elif difficulty == "hard":
        num_cells = random.randint(56, 62) #19 to 25 clues
    elif difficulty == "secret":
        num_cells = random.randint(2, 2) #TESTING MODE
    else:
        num_cells = random.randint(63, 64) #EVIL mode 17 to 18 clues

    return num_cells

#pattern for a baseline valid solution
def pattern(r, c): 
    return (base * (r % base) + r // base + c) % side

#randomize rows, columns and numbers (of valid base pattern)
def shuffle(s): 
    return sample(s, len(s))

rBase = range(base)
rows = [g * base + r for g in shuffle(rBase) for r in shuffle(rBase)]
cols = [g * base + c for g in shuffle(rBase) for c in shuffle(rBase)]
nums = shuffle(range(1, base * base + 1))

#produce board using randomized baseline pattern
board = [[nums[pattern(r, c)] for c in cols] for r in rows]
boardCopy = [[nums[pattern(r, c)] for c in cols] for r in rows]
    
squares = side * side
empties = difficulty_set()
clue_numbers = 81 - empties


print("Empty squares:", empties)
print("Amount of clue numbers:", clue_numbers)

for p in sample(range(squares), empties):
    board[p//side][p % side] = 0
    
numSize = len(str(side))

def print_board(stdscr, board, cursor):
    os.system("cls")
    stdscr.clear()

    box_top_left = "╔"
    box_top_right = "╗"
    box_bottom_left = "╚"
    box_bottom_right = "╝"
    box_horizontal = "═" * 3
    box_vertical = "║"
    box_intersection = "╬"
    box_left_intersection = "╠"
    box_right_intersection = "╣"
    box_top_intersection = "╦"
    box_bottom_intersection = "╩"

    #print the top border of the box
    stdscr.addstr(box_top_left + box_horizontal * 3 + box_top_intersection + box_horizontal * 3 + box_top_intersection + box_horizontal * 3 + box_top_right + "\n")

    for i in range(9):
        #print the left border of the box
        stdscr.addstr(box_vertical)

        for j in range(9):
            #print the value of the cell
            if (i, j) == cursor:
                stdscr.addstr(f" {board[i][j]} ", curses.A_REVERSE)
            else:
                stdscr.addstr(f" {board[i][j]} ")

            #print the vertical lines between boxes
            if j == 2 or j == 5:
                stdscr.addstr(box_vertical)

        #print the right border of the box
        stdscr.addstr(box_vertical + "\n")

        #print the horizontal lines between boxes
        if i == 2 or i == 5:
            stdscr.addstr(box_left_intersection + box_horizontal * 3 + box_intersection + box_horizontal * 3 + box_intersection + box_horizontal * 3 + box_right_intersection + "\n")

    stdscr.addstr(box_bottom_left + box_horizontal * 3 + box_bottom_intersection + box_horizontal * 3 + box_bottom_intersection + box_horizontal * 3 + box_bottom_right + "\n")
    
    stdscr.addstr("> Press 'Q' to quit at anytime!" + "\n")
    
    stdscr.addstr("> Press 'E' to check if the solution is correct")
    stdscr.refresh()

def check_solution(grid, solution):
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0 and grid[i][j] != solution[i][j]:
                return False
    return True

def move_cursor(cursor, direction):
    i, j = cursor
    if direction == curses.KEY_UP and i > 0:
        i -= 1
    elif direction == curses.KEY_DOWN and i < 8:
        i += 1
    elif direction == curses.KEY_LEFT and j > 0:
        j -= 1
    elif direction == curses.KEY_RIGHT and j < 8:
        j += 1
    return (i, j)

def is_identical(list1, list2):
    if len(list1) != len(list2):
        return False
    for i in range(len(list1)):
        if len(list1[i]) != len(list2[i]):
            return False
        for j in range(len(list1[i])):
            if list1[i][j] != list2[i][j]:
                return False
    return True

def play_sudoku(stdscr):
    stdscr = curses.initscr()
    cursor = (0, 0)
    print_board(stdscr, board, cursor)
    while True:
        key = stdscr.getch()
        #move cursor if arrow key is pressed
        if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
            cursor = move_cursor(cursor, key)
            print_board(stdscr, board, cursor)

        #add number to board if number key is pressed
        elif key in [ord(str(i)) for i in range(0, 10)]:
            i, j = cursor
            board[i][j] = int(chr(key)) #update the board
            print_board(stdscr, board, cursor) #pass the updated board to print_board
            bad_numbers()
        elif key == 101:
            if is_identical(board, boardCopy):
                win_screen()
                return
            else:
                print(f"INCORRECT SOLUTION!")
        elif key == 113:
            exit_screen()
            return

def bad_numbers():
    #check rof for duplicates
    for row in board:
        num_counts = {}
        for num in row:
            if num != 0:
                if num in num_counts:
                    print(f"Duplicate number {num} in row {row}")
                else:
                    num_counts[num] = 1
    
    #check 3x3 for duplicates
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            num_counts = {}
            for row in range(box_row, box_row+3):
                for col in range(box_col, box_col+3):
                    num = board[row][col]
                    if num != 0:
                        if num in num_counts:
                            print(f"Duplicate number {num} in 3x3 box starting at row {box_row} and column {box_col}")
                        else:
                            num_counts[num] = 1

def exit_screen():
    curses.endwin()
    os.system("cls")
    time.sleep(0.5)
    print(f"{lightcyan}> {RESA}Correct solution:")
    for line in boardCopy:
        print(line)
    input(f"{lightcyan}> {RESA}Thank you for playing Sudoku! Press '{FAIL}enter{RESA}' to exit.")

def win_screen():
    curses.endwin()
    os.system("cls")
    time.sleep(0.5)
    print(f"{lightcyan}> {RESA}That was correct!")
    for line in boardCopy:
        print(line)
    input(f"{lightcyan}> {RESA}Thank you for playing Sudoku! Press '{FAIL}enter{RESA}' to exit.")
        
def main():
    curses.wrapper(play_sudoku)
    
if __name__ == '__main__':
    main() 
    curses.endwin()
