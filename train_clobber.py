# importing libraries
import os
import random
import time

initial_pos = 'a;bb a;b'  # initial position of play
r = 2  # no of rows of clobber board
c = 2  # no of columns of clobber board
iterations = 1000  # no of iterations the game is played for training
dir_name = str(r)+'x'+str(c)

possible_moves_a = {}  # stores all possible options for player A from a position
possible_moves_b = {}  # stores all possible options for player B from a position
count_a_first = 0  # counts winning positions for player A when A plays first
count_b_first = 0  # counts winning positions for player B when B plays first
count_a_second = 0  # counts winning positions for player A when A plays second
count_b_second = 0  # counts winning positions for player B when B plays second
beliefs = {}  # stores belief values for both player A and player B

opening_p = []  # stores all opening moves
terminal_p = []  # stores all terminal moves


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


# the following function simulates a single play of clobber
def play(pos, m, n):
    global possible_moves_a
    global possible_moves_b
    global count_a_first
    global count_b_first
    global count_a_second
    global count_b_second
    global beliefs

    update_a = []  # stores all played moves of player A
    update_b = []  # stores all played moves of player B
    end = 0  # trigger variable to denote when game ends
    turn = random.choice(['a', 'b'])  # represents whose turn it is
    first = turn  # stores the player that plays first
    initial_p = pos  # stores the position

    opening_marker = 0

    while end == 0:
        temp_options_a = []  # temporary options from the specific position for player A
        temp_options_b = []  # temporary options from the specific position for player B
        end = 1  # trigger variable

        # checks whether current position is symmetric to any already traversed positions
        if turn == 'a':
            check, initial_p = check_symmetry(initial_p, possible_moves_a)
        elif turn == 'b':
            check, initial_p = check_symmetry(initial_p, possible_moves_b)

        # if position already traversed then next position is calculated from stored belief values
        if turn == 'a' and check:
            initial_p = make_string(
                possible_moves_a[initial_p][weighted_average(possible_moves_a[initial_p], beliefs, turn)])
            update_a.append(initial_p)
            end = 0
            if opening_marker == 0:
                check, pos_str = check_symmetry(initial_p, opening_p)
                if not check:
                    opening_p.append(pos_str)
                opening_marker = 1
            turn = 'b'

        elif turn == 'b' and check:
            initial_p = make_string(
                possible_moves_b[initial_p][weighted_average(possible_moves_b[initial_p], beliefs, turn)])
            update_b.append(initial_p)
            end = 0
            if opening_marker == 0:
                check, pos_str = check_symmetry(initial_p, opening_p)
                if not check:
                    opening_p.append(pos_str)
                opening_marker = 1
            turn = 'a'

        # if position has not been traversed then all options are calculated and stored
        else:
            initial_p = [i.split(';') for i in initial_p.split(' ')]  # changing string position to list form
            for i in range(m):  # traversing over all blocks on the board
                for j in range(n):
                    if turn in initial_p[i][j]:
                        case = 4  # there are at most 4 ways a piece can move
                        while case > 0:
                            temp_pos = [i.copy() for i in initial_p]
                            if case == 4:
                                if i+1 < m:
                                    if temp_pos[i+1][j] == '0':
                                        pass
                                    elif temp_pos[i+1][j][0] == temp_pos[i][j][0]:
                                        temp_pos[i+1][j] += temp_pos[i][j]
                                        temp_pos[i][j] = '0'
                                    else:
                                        if len(temp_pos[i+1][j]) <= len(temp_pos[i][j]):
                                            temp_pos[i+1][j] = temp_pos[i][j]
                                            temp_pos[i][j] = '0'
                                if 'a' in initial_p[i][j] and temp_pos != initial_p:
                                    end = 0
                                    temp_pos_str = make_string(temp_pos)
                                    check, temp_pos_str = check_symmetry(temp_pos_str, temp_options_a)
                                    if not check:
                                        temp_options_a.append(temp_pos)
                                    check, temp_pos_str = check_symmetry(temp_pos_str, beliefs)
                                    if not check:
                                        beliefs[temp_pos_str] = [0.5, 0.5]
                                elif 'b' in initial_p[i][j] and temp_pos != initial_p:
                                    end = 0
                                    temp_pos_str = make_string(temp_pos)
                                    check, temp_pos_str = check_symmetry(temp_pos_str, temp_options_b)
                                    if not check:
                                        temp_options_b.append(temp_pos)
                                    check, temp_pos_str = check_symmetry(temp_pos_str, beliefs)
                                    if not check:
                                        beliefs[temp_pos_str] = [0.5, 0.5]

                            elif case == 3:
                                if i-1 >= 0:
                                    if temp_pos[i-1][j] == '0':
                                        pass
                                    elif temp_pos[i-1][j][0] == temp_pos[i][j][0]:
                                        temp_pos[i-1][j] += temp_pos[i][j]
                                        temp_pos[i][j] = '0'
                                    else:
                                        if len(temp_pos[i-1][j]) <= len(temp_pos[i][j]):
                                            temp_pos[i-1][j] = temp_pos[i][j]
                                            temp_pos[i][j] = '0'
                                if 'a' in initial_p[i][j] and temp_pos != initial_p:
                                    end = 0
                                    temp_pos_str = make_string(temp_pos)
                                    check, temp_pos_str = check_symmetry(temp_pos_str, temp_options_a)
                                    if not check:
                                        temp_options_a.append(temp_pos)
                                    check, temp_pos_str = check_symmetry(temp_pos_str, beliefs)
                                    if not check:
                                        beliefs[temp_pos_str] = [0.5, 0.5]
                                elif 'b' in initial_p[i][j] and temp_pos != initial_p:
                                    end = 0
                                    temp_pos_str = make_string(temp_pos)
                                    check, temp_pos_str = check_symmetry(temp_pos_str, temp_options_b)
                                    if not check:
                                        temp_options_b.append(temp_pos)
                                    check, temp_pos_str = check_symmetry(temp_pos_str, beliefs)
                                    if not check:
                                        beliefs[temp_pos_str] = [0.5, 0.5]

                            elif case == 2:
                                if j-1 >= 0:
                                    if temp_pos[i][j-1] == '0':
                                        pass
                                    elif temp_pos[i][j-1][0] == temp_pos[i][j][0]:
                                        temp_pos[i][j-1] += temp_pos[i][j]
                                        temp_pos[i][j] = '0'
                                    else:
                                        if len(temp_pos[i][j-1]) <= len(temp_pos[i][j]):
                                            temp_pos[i][j-1] = temp_pos[i][j]
                                            temp_pos[i][j] = '0'
                                if 'a' in initial_p[i][j] and temp_pos != initial_p:
                                    end = 0
                                    temp_pos_str = make_string(temp_pos)
                                    check, temp_pos_str = check_symmetry(temp_pos_str, temp_options_a)
                                    if not check:
                                        temp_options_a.append(temp_pos)
                                    check, temp_pos_str = check_symmetry(temp_pos_str, beliefs)
                                    if not check:
                                        beliefs[temp_pos_str] = [0.5, 0.5]
                                elif 'b' in initial_p[i][j] and temp_pos != initial_p:
                                    end = 0
                                    temp_pos_str = make_string(temp_pos)
                                    check, temp_pos_str = check_symmetry(temp_pos_str, temp_options_b)
                                    if not check:
                                        temp_options_b.append(temp_pos)
                                    check, temp_pos_str = check_symmetry(temp_pos_str, beliefs)
                                    if not check:
                                        beliefs[temp_pos_str] = [0.5, 0.5]

                            elif case == 1:
                                if j+1 < n:
                                    if temp_pos[i][j+1] == '0':
                                        pass
                                    elif temp_pos[i][j+1][0] == temp_pos[i][j][0]:
                                        temp_pos[i][j+1] += temp_pos[i][j]
                                        temp_pos[i][j] = '0'
                                    else:
                                        if len(temp_pos[i][j+1]) <= len(temp_pos[i][j]):
                                            temp_pos[i][j+1] = temp_pos[i][j]
                                            temp_pos[i][j] = '0'
                                if 'a' in initial_p[i][j] and temp_pos != initial_p:
                                    end = 0
                                    temp_pos_str = make_string(temp_pos)
                                    check, temp_pos_str = check_symmetry(temp_pos_str, temp_options_a)
                                    if not check:
                                        temp_options_a.append(temp_pos)
                                    check, temp_pos_str = check_symmetry(temp_pos_str, beliefs)
                                    if not check:
                                        beliefs[temp_pos_str] = [0.5, 0.5]
                                elif 'b' in initial_p[i][j] and temp_pos != initial_p:
                                    end = 0
                                    temp_pos_str = make_string(temp_pos)
                                    check, temp_pos_str = check_symmetry(temp_pos_str, temp_options_b)
                                    if not check:
                                        temp_options_b.append(temp_pos)
                                    check, temp_pos_str = check_symmetry(temp_pos_str, beliefs)
                                    if not check:
                                        beliefs[temp_pos_str] = [0.5, 0.5]
                            case -= 1

            pos_str = make_string(initial_p)

            if end == 1:
                if pos_str not in terminal_p:
                    terminal_p.append(pos_str)

            # updating possible options from current position for both players
            if len(temp_options_a) != 0:
                possible_moves_a[pos_str] = temp_options_a
            if len(temp_options_b) != 0:
                possible_moves_b[pos_str] = temp_options_b

            # updating current position and changing turn
            if turn == 'a' and len(temp_options_a) != 0:
                initial_p = temp_options_a[weighted_average(temp_options_a, beliefs, turn)]
                initial_p = make_string(initial_p)
                update_a.append(initial_p)
                turn = 'b'

            elif turn == 'b' and len(temp_options_b) != 0:
                initial_p = temp_options_b[weighted_average(temp_options_b, beliefs, turn)]
                initial_p = make_string(initial_p)
                update_b.append(initial_p)
                turn = 'a'

            if opening_marker == 0:
                check, p = check_symmetry(initial_p, opening_p)
                if not check:
                    opening_p.append(p)
                opening_marker = 1

    # updating win no's and updating belief
    if turn == 'a':
        if first == 'b':
            count_b_first += 1
        elif first == 'a':
            count_b_second += 1

        for i in update_b:
            check, i = check_symmetry(i, beliefs)
            beliefs[i][1] = (beliefs[i][1] + 1)/2

        for i in update_a:
            check, i = check_symmetry(i, beliefs)
            beliefs[i][0] = (beliefs[i][0])/2

    elif turn == 'b':
        if first == 'a':
            count_a_first += 1
        elif first == 'b':
            count_a_second += 1

        for i in update_b:
            check, i = check_symmetry(i, beliefs)
            beliefs[i][1] = (beliefs[i][1])/2

        for i in update_a:
            check, i = check_symmetry(i, beliefs)
            beliefs[i][0] = (beliefs[i][0] + 1)/2


mod = iterations // 10
start_time = time.time()
for k in range(iterations):
    if k % mod == 0:
        print(k)
    play(initial_pos, r, c)
end_time = time.time()

if not os.path.isdir(dir_name):
    os.makedirs(dir_name)

file_path = os.getcwd()+'/'+dir_name+'/'

file_a = open(file_path+'beliefs'+'_'+dir_name+'.txt', 'wt')
for key, value in beliefs.items():
    file_a.write('%s:%s\n' % (key, value))
file_a.close()

file_b = open(file_path+'possible_moves_a'+'_'+dir_name+'.txt', 'wt')
for key, value in possible_moves_a.items():
    file_b.write('%s:%s\n' % (key, value))
file_a.close()

file_c = open(file_path+'possible_moves_b'+'_'+dir_name+'.txt', 'wt')
for key, value in possible_moves_b.items():
    file_c.write('%s:%s\n' % (key, value))
file_c.close()

file_d = open(file_path+'opening'+'_'+dir_name+'.txt', 'wt')
for k in opening_p:
    _, k = check_symmetry(k, beliefs)
    file_d.write('%s:%s\n' % (k, beliefs[k]))
file_d.close()

file_e = open(file_path+'terminal'+'_'+dir_name+'.txt', 'wt')
for k in terminal_p:
    _, k = check_symmetry(k, beliefs)
    file_e.write('%s:%s\n' % (k, beliefs[k]))
file_e.close()

file_f = open(file_path+'stats_'+dir_name+'.txt', 'wt')
file_f.write('No. of iterations: ' + str(iterations))
file_f.write('\nTime taken: ' + str(end_time - start_time))
file_f.write('\nNo. of times A wins while playing first: ' + str(count_a_first) + '\nNo. of times B wins while playing first: ' + str(count_b_first) + '\nNo. of times A wins while playing second: ' + str(count_a_second) + '\nNo. of times B wins while playing second: ' + str(count_b_second))
file_f.close()


