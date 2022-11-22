#importing libraries
import os
import ast
import random
import time

start_time = time.time()

initial_pos = 'bb;a b;a'  # initial position of play
r = 2  # no of rows of clobber board
c = 2  # no of columns of clobber board
dir_name = str(r)+'x'+str(c)


# the following function uploads the trained beliefs from the file system
def update_belief(d, h):
    if os.path.exists(h):
        with open(h) as f:
            for line in f:
                key = line.split(':')[0]
                value = ast.literal_eval(line.split(':')[1])
                d[key] = value


# the following function uploads the trained possible moves from the file system
def update_moves(d, h):
    if os.path.exists(h):
        with open(h) as f:
            for line in f:
                key = line.split(':')[0]
                value = ast.literal_eval(line.split(':')[1])
                d[key] = value


# the following function makes a probability distribution over viable options and picks one
def weighted_average(options, belief, turn):
    if turn == 'a':
        turn = 0
    else:
        turn = 1

    n = len(options)
    sum_of_beliefs = 0
    for i in options:
        check, i = check_symmetry(make_string(i), belief)
        sum_of_beliefs += belief[i][turn]

    prob_dist = []
    if sum_of_beliefs != 0:
        for i in options:
            check, i = check_symmetry(make_string(i), belief)
            prob_dist.append(belief[i][turn]/sum_of_beliefs)

        return random.choices([i for i in range(n)], prob_dist)[0]
    else:
        return random.choice([i for i in range(n)])


# the following function converts a position in list form to a string
def make_string(pos):
    pos_c = [row.copy() for row in pos]
    for i in range(len(pos_c)):
        pos_c[i] = ';'.join(pos_c[i])
    pos_c = ' '.join(pos_c)
    return pos_c


# the following function horizontally reverses the position
def reverse_horizontal(pos):
    pos = [i.split(';') for i in pos.split(' ')]
    rev_pos = []
    for i in pos:
        rev_pos.append(i[::-1])
    return make_string(rev_pos)


# the following function vertically reverses the position
def reverse_vertical(pos):
    pos = [i.split(';') for i in pos.split(' ')]
    rev_pos = pos[::-1]
    return make_string(rev_pos)


# the following function rotates a position by 90 degrees
def rotate(pos):
    pos = [i.split(';') for i in pos.split(' ')]
    sym_pos = []
    for j in range(len(pos[0])):
        row = []
        for i in range(len(pos)-1, -1, -1):
            row.append(pos[i][j])
        sym_pos.append(row)
    return make_string(sym_pos)


# the following function checks if a symmetrical position has already been traversed
def check_symmetry(pos, dic):
    for i in range(4):
        pos_rev_hr = reverse_horizontal(pos)
        pos_rev_vr = reverse_vertical(pos)
        if pos in dic:
            return True, pos
        if pos_rev_hr in dic:
            return True, pos_rev_hr
        if reverse_vertical(pos) in dic:
            return True, pos_rev_vr
        pos = rotate(pos)
    return False, pos


file_path = os.getcwd()+'/'+dir_name+'/'

possible_moves_a = {}  # stores all possible options for player A from a position
possible_moves_b = {}  # stores all possible options for player B from a position
update_moves(possible_moves_a, file_path+'possible_moves_a'+'_'+dir_name+'.txt')  # moves of player A uploaded
update_moves(possible_moves_b, file_path+'possible_moves_b'+'_'+dir_name+'.txt')  # moves of player B uploaded

beliefs = {}  # stores belief values for both player A and player B
update_belief(beliefs, file_path+'beliefs'+'_'+dir_name+'.txt')  # belief values uploaded


end = 0
turn = random.choice(['a', 'b'])

play = input('Would you like to play against the bot?(Y/N)\n')

if play == 'Y':
    human = input('Would you like to play as A or B?(A/B)')
    while end == 0:
        end = 1
        print(turn + ' : ' + initial_pos)
        if turn == 'a':
            if human == 'A':
                check, initial_pos = check_symmetry(initial_pos, possible_moves_a)
                if check:
                    initial_pos = input()
                    end = 0
                    turn = 'b'
            else:
                check, initial_pos = check_symmetry(initial_pos, possible_moves_a)
                if check:
                    initial_pos = make_string(
                        possible_moves_a[initial_pos][weighted_average(possible_moves_a[initial_pos], beliefs, turn)])
                    end = 0
                    turn = 'b'
        elif turn == 'b':
            if human == 'B':
                check, initial_pos = check_symmetry(initial_pos, possible_moves_b)
                if check:
                    initial_pos = input()
                    end = 0
                    turn = 'a'
            else:
                check, initial_pos = check_symmetry(initial_pos, possible_moves_b)
                if check:
                    initial_pos = make_string(
                        possible_moves_b[initial_pos][weighted_average(possible_moves_b[initial_pos], beliefs, turn)])
                    end = 0
                    turn = 'a'

else:
    while end == 0:
        end = 1
        print(turn + ' : ' + initial_pos)
        if turn == 'a':
            check, initial_pos = check_symmetry(initial_pos, possible_moves_a)
        elif turn == 'b':
            check, initial_pos = check_symmetry(initial_pos, possible_moves_b)

        if turn == 'a' and check:
            initial_pos = make_string(
                possible_moves_a[initial_pos][weighted_average(possible_moves_a[initial_pos], beliefs, turn)])
            end = 0
            turn = 'b'

        elif turn == 'b' and check:
            initial_pos = make_string(
                possible_moves_b[initial_pos][weighted_average(possible_moves_b[initial_pos], beliefs, turn)])
            end = 0
            turn = 'a'

if turn == 'a':
    print('B WINS')
else:
    print('A WINS')



