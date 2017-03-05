#!/usr/bin/python
# Assignment 4: Cuckoo Hashing
# Curtis Galvez
# https://docs.google.com/document/d/1cOJzZ2eM6oKXp-bFVoAiOL9opg3Q9DcwHMrx4VyMFTQ/edit?pref=2&pli=1
# INPUT: an input file containing strings of characters, one string per line
# OUTPUT: a detailed list of where the strings are inserted.
import sys

def read_file(file_name):
    with open(file_name, 'r') as f:
        words = f.readlines()
    return words

def hash_me(word, rows, hash_index):
    if hash_index == 0:
        word_value = ord(word[0]) % rows
        for index, character in enumerate(word[1:len(word)]):
            word_value += (ord(character) % rows) * (31**(index+1))
    else:
        word_value = 0
        word_size = len(word)
        for index, character in enumerate(word):
            word_value += (ord(character) % rows) * (31**(word_size-index-1))
    return word_value % rows

def left_pad(word_one, word_two, table, longest_word):
    padding = ' '
    if len(word_one) < longest_word:
        for i in range(longest_word-len(word_one)):
            padding += ' '
    padding += '\t'
    return '{0}{1}{2}'.format(word_one, padding, word_two)

def main():
    columns, rows = 2, 17

    # rows, columns = int(input('enter number of rows: ')), int(input('enter number of columns: '))
    table = [[0 for j in range(rows)] for i in range(columns)]

    if sys.version_info.major == 3:
        words = read_file(input('Input the file name (no spaces)! '))
    elif sys.version_info.major == 2:
        words = read_file(raw_input('Input the file name (no spaces)! '))
    else:
        print('Please use Python 2 or Python 3')
        sys.exit(1)

    longest_word = len(words[0])
    print('CPSC 335-x - Programming Assignment #4: Cuckoo Hashing algorithm')
    for word in words:
        word = word.rstrip('\n\r')
        if len(word) > longest_word:
            longest_word = len(word)
        hash_index = hash_me(word, rows, 0)
        count = 0
        placed = False
        index = 0
        while not placed and count < 2 * rows:
            if (table[index][hash_index] == 0):
                print('String <{0}> will be placed at t[{1}][{2}]'.format(word, hash_index, index))
                table[index][hash_index] = word
                placed = True
            else:
                temp_word = table[index][hash_index]
                print('String <{0}> will be placed at t[{1}][{2}] replacing <{3}>'.format(word, hash_index, index, temp_word))
                table[index][hash_index] = word
                word = temp_word
                if index == 0:
                    index = 1
                else:
                    index = 0
                hash_index = hash_me(word, rows, index)
                count += 1
            if count == 2 * rows - 1:
                print('Placement failed: {0}'.format(temp_word))

    print('\n')
    html = '<html><body><table border="1"><tr><td></td><td>Table T1</td><td>Table T2</td></tr>'
    for row in range(rows):
        if str(table[0][row]) == '0':
            table[0][row] = ''
        if str(table[1][row]) == '0':
            table[1][row] = ''
        html += '<tr><td>[{0}]</td><td>{1}</td><td>{2}</td></tr>'.format(row, table[0][row], table[1][row])
        print(left_pad(str(table[0][row]), table[1][row], table, longest_word))
    html += '</table></body></html>'
    with open('output.html', 'w') as f:
        f.write(html)

if __name__ == '__main__':
    main()
