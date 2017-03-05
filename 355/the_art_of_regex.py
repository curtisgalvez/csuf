import re
import string
import time

def main():
    start = time.time()
    with open('input', 'r') as f:
        text = f.read()
    # text = re.sub('(\[\d.*\d\])', ' ', text)        # replace all elements matching [##.##]
    # text = re.sub('[\[\]\';:,.()\-"!?]', ' ', text) # replace all characters matching: ';:,.()-
    # text = re.sub('\d', ' ', text)                  # replace all numbers
	text = re.sub('([^a-zA-Z\s\'])', ' ', text)       # replace all characters not alpha, whitespace, or '
	text = re.sub('([\'])', '', text)                 # replace all ' with no space
    alpha_dict = alpha_frequency(text)
    word_dict = word_frequency(text)
    results(alpha_dict, word_dict, longest_word(word_dict))
    print(str(time.time()-start))

def word_frequency(text):
    # add all the words to a dictionary and increment count if it exists in dictionary
    word_dict = {}
    for word in text.split():
        if len(word) > 0:
            if word.lower() in word_dict:
                word_dict[word.lower()] += 1
            else:
                word_dict.update({word.lower(): 1})
    return word_dict

def alpha_frequency(text):
    # get character frequency for alphabet
    alpha_dict = {}
    for alpha in string.ascii_lowercase:
        alpha_dict.update({alpha.lower(): len(re.findall('([{0}{1}])'.format(alpha, alpha.upper()), text))})
    return alpha_dict

def longest_word(word_dict):
    # find the longest word(s) in the text
    long_word = ['']
    for word in word_dict:
        if len(word) > len(long_word[0]):
            long_word = []
            long_word.append(word)
        elif len(word) == len(long_word[0]):
            long_word.append(word)
    return long_word

def results(alpha_dict, word_dict, long_word):
    print('Letter frequency:')
    # [print '\t{0} - {1}'.format(alpha, alpha_dict[alpha]) for alpha in sorted(alpha_dict)]
    for alpha in sorted(alpha_dict):
        print '\t{0} - {1}'.format(alpha, alpha_dict[alpha])
    print('The word \'the\' appears {0} times'.format(word_dict['the']))
    print('The world \'principles\' appears {0} times'.format(word_dict['principles']))
    print('The longest word(s) at length {0}:'.format(len(long_word[0])))
    # [print('\t', word) for word in long_word]
    for word in long_word:
        print('\t{0}'.format(word))

if __name__ == '__main__':
	main()