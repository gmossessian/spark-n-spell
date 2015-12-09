'''
serial_listsugg.py

################

To run, execute python serial_listsugg.py at the prompt.
Make sure the dictionary "big.txt" is in the current working directory.
Enter word to correct when prompted.

################

v 1.0 last revised 22 Nov 2015

This program is a Python version of a spellchecker based on SymSpell, 
a Symmetric Delete spelling correction algorithm developed by Wolf Garbe 
and originally written in C#.

From the original SymSpell documentation:

"The Symmetric Delete spelling correction algorithm reduces the complexity 
 of edit candidate generation and dictionary lookup for a given Damerau-
 Levenshtein distance. It is six orders of magnitude faster and language 
 independent. Opposite to other algorithms only deletes are required, 
 no transposes + replaces + inserts. Transposes + replaces + inserts of the 
 input term are transformed into deletes of the dictionary term.
 Replaces and inserts are expensive and language dependent: 
 e.g. Chinese has 70,000 Unicode Han characters!"

For further information on SymSpell, please consult the original documentation:
  URL: blog.faroo.com/2012/06/07/improved-edit-distance-based-spelling-correction/
  Description: blog.faroo.com/2012/06/07/improved-edit-distance-based-spelling-correction/

The current version of this program will output all possible suggestions for
corrections up to an edit distance (configurable) of max_edit_distance = 3. 

Future improvements may entail allowing for less verbose options, 
including the output of a single recommended correction. Note also that we
have generally kept to the form of the original program, and have not
introduced any major optimizations or structural changes in this Python port.


################

Example output:

################

# word input (call to get_suggestions)

number of possible corrections: 604
  edit distance for deletions: 3
  
[('there', (2972, 0)),
 ('these', (1231, 1)),
 ('where', (977, 1)),
 ('here', (691, 1)),
 ('three', (584, 1)),
 ('thee', (26, 1)),
 ('chere', (9, 1)),
 ('theme', (8, 1)),
 ('the', (80030, 2)), ...

####

# document input (call to correct_document)

Finding misspelled words in your document...
In line 3, taiths: suggested correction is < faith >
In line 11, the word < oonipiittee > was not found (no suggested correction)
In line 13, tj: suggested correction is < to >
In line 13, mnnff: suggested correction is < snuff >
[...]

total words checked: 700
total unknown words: 3
total potential errors found: 94

'''

import re

max_edit_distance = 3 

dictionary = {}
longest_word_length = 0

def get_deletes_list(w):
    '''given a word, derive strings with up to max_edit_distance characters deleted'''
    deletes = []
    queue = [w]
    for d in range(max_edit_distance):
        temp_queue = []
        for word in queue:
            if len(word)>1:
                for c in range(len(word)):  # character index
                    word_minus_c = word[:c] + word[c+1:]
                    if word_minus_c not in deletes:
                        deletes.append(word_minus_c)
                    if word_minus_c not in temp_queue:
                        temp_queue.append(word_minus_c)
        queue = temp_queue
        
    return deletes

def create_dictionary_entry(w):
    '''add word and its derived deletions to dictionary'''
    # check if word is already in dictionary
    # dictionary entries are in the form: (list of suggested corrections, frequency of word in corpus)
    global longest_word_length
    new_real_word_added = False
    if w in dictionary:
        dictionary[w] = (dictionary[w][0], dictionary[w][1] + 1)  # increment count of word in corpus
    else:
        dictionary[w] = ([], 1)  
        longest_word_length = max(longest_word_length, len(w))
        
    if dictionary[w][1]==1:
        # first appearance of word in corpus
        # n.b. word may already be in dictionary as a derived word (deleting character from a real word)
        # but counter of frequency of word in corpus is not incremented in those cases)
        new_real_word_added = True
        deletes = get_deletes_list(w)
        for item in deletes:
            if item in dictionary:
                # add (correct) word to delete's suggested correction list if not already there
                if item not in dictionary[item][0]:
                    dictionary[item][0].append(w)
            else:
                dictionary[item] = ([w], 0)  # note frequency of word in corpus is not incremented
        
    return new_real_word_added

def create_dictionary(fname):

    total_word_count = 0
    unique_word_count = 0
    print "Creating dictionary..." 
    
    with open(fname) as file:    
        for line in file:
            words = re.findall('[a-z]+', line.lower())  # separate by words by non-alphabetical characters      
            for word in words:
                total_word_count += 1
                if create_dictionary_entry(word):
                    unique_word_count += 1
    
    print "total words processed: %i" % total_word_count
    print "total unique words in corpus: %i" % unique_word_count
    print "total items in dictionary (corpus words and deletions): %i" % len(dictionary)
    print "  edit distance for deletions: %i" % max_edit_distance
    print "  length of longest word in corpus: %i" % longest_word_length
        
    return dictionary

def dameraulevenshtein(seq1, seq2):
    """Calculate the Damerau-Levenshtein distance between sequences.

    This method has not been modified from the original.
    Source: http://mwh.geek.nz/2009/04/26/python-damerau-levenshtein-distance/
    
    This distance is the number of additions, deletions, substitutions,
    and transpositions needed to transform the first sequence into the
    second. Although generally used with strings, any sequences of
    comparable objects will work.

    Transpositions are exchanges of *consecutive* characters; all other
    operations are self-explanatory.

    This implementation is O(N*M) time and O(M) space, for N and M the
    lengths of the two sequences.

    >>> dameraulevenshtein('ba', 'abc')
    2
    >>> dameraulevenshtein('fee', 'deed')
    2

    It works with arbitrary sequences too:
    >>> dameraulevenshtein('abcd', ['b', 'a', 'c', 'd', 'e'])
    2
    """
    # codesnippet:D0DE4716-B6E6-4161-9219-2903BF8F547F
    # Conceptually, this is based on a len(seq1) + 1 * len(seq2) + 1 matrix.
    # However, only the current and two previous rows are needed at once,
    # so we only store those.
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        # Python lists wrap around for negative indices, so put the
        # leftmost column at the *end* of the list. This matches with
        # the zero-indexed strings and saves extra calculation.
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
            # This block deals with transpositions
            if (x > 0 and y > 0 and seq1[x] == seq2[y - 1]
                and seq1[x-1] == seq2[y] and seq1[x] != seq2[y]):
                thisrow[y] = min(thisrow[y], twoago[y - 2] + 1)
    return thisrow[len(seq2) - 1]

def get_suggestions(string, silent=False):
    '''return list of suggested corrections for potentially incorrectly spelled word'''
    if (len(string) - longest_word_length) > max_edit_distance:
        if not silent:
            print "no items in dictionary within maximum edit distance"
        return []
    
    suggest_dict = {}
    
    queue = [string]
    q_dictionary = {}  # items other than string that we've checked
    
    while len(queue)>0:
        q_item = queue[0]  # pop
        queue = queue[1:]
        
        # process queue item
        if (q_item in dictionary) and (q_item not in suggest_dict):
            if (dictionary[q_item][1]>0):
            # word is in dictionary, and is a word from the corpus, and not already in suggestion list
            # so add to suggestion dictionary, indexed by the word with value (frequency in corpus, edit distance)
            # note q_items that are not the input string are shorter than input string 
            # since only deletes are added (unless manual dictionary corrections are added)
                assert len(string)>=len(q_item)
                suggest_dict[q_item] = (dictionary[q_item][1], len(string) - len(q_item))
            
            ## the suggested corrections for q_item as stored in dictionary (whether or not
            ## q_item itself is a valid word or merely a delete) can be valid corrections
            for sc_item in dictionary[q_item][0]:
                if (sc_item not in suggest_dict):
                    
                    # compute edit distance
                    # suggested items should always be longer (unless manual corrections are added)
                    assert len(sc_item)>len(q_item)
                    # q_items that are not input should be shorter than original string 
                    # (unless manual corrections added)
                    assert len(q_item)<=len(string)
                    if len(q_item)==len(string):
                        assert q_item==string
                        item_dist = len(sc_item) - len(q_item)

                    # item in suggestions list should not be the same as the string itself
                    assert sc_item!=string           
                    # calculate edit distance using, for example, Damerau-Levenshtein distance
                    item_dist = dameraulevenshtein(sc_item, string)
                    
                    if item_dist<=max_edit_distance:
                        assert sc_item in dictionary  # should already be in dictionary if in suggestion list
                        suggest_dict[sc_item] = (dictionary[sc_item][1], item_dist)
        
        # now generate deletes (e.g. a substring of string or of a delete) from the queue item
        # as additional items to check -- add to end of queue
        assert len(string)>=len(q_item)
        if (len(string)-len(q_item))<max_edit_distance and len(q_item)>1:
            for c in range(len(q_item)): # character index        
                word_minus_c = q_item[:c] + q_item[c+1:]
                if word_minus_c not in q_dictionary:
                    queue.append(word_minus_c)
                    q_dictionary[word_minus_c] = None  # arbitrary value, just to identify we checked this
             
    # queue is now empty: convert suggestions in dictionary to list for output
    if not silent:
        print "number of possible corrections: %i" %len(suggest_dict)
        print "  edit distance for deletions: %i" % max_edit_distance
    
    # output option 1
    # sort results by ascending order of edit distance and descending order of frequency
    #     and return list of suggested word corrections only:
    # return sorted(suggest_dict, key = lambda x: (suggest_dict[x][1], -suggest_dict[x][0]))

    # output option 2
    # return list of suggestions with (correction, (frequency in corpus, edit distance)):
    as_list = suggest_dict.items()
    return sorted(as_list, key = lambda (term, (freq, dist)): (dist, -freq))

    '''
    Option 1:
    get_suggestions("file")
    ['file', 'five', 'fire', 'fine', ...]
    
    Option 2:
    get_suggestions("file")
    [('file', (5, 0)),
     ('five', (67, 1)),
     ('fire', (54, 1)),
     ('fine', (17, 1))...]  
    '''

def best_word(s, silent=False):
    try:
        return get_suggestions(s, silent)[0]
    except:
        return None
    
def correct_document(fname, printlist=True):
    # correct an entire document
    with open(fname) as file:
        doc_word_count = 0
        corrected_word_count = 0
        unknown_word_count = 0
        print "Finding misspelled words in your document..." 
        
        for i, line in enumerate(file):
            doc_words = re.findall('[a-z]+', line.lower())  # separate by words by non-alphabetical characters      
            for doc_word in doc_words:
                doc_word_count += 1
                suggestion = best_word(doc_word, silent=True)
                if suggestion is None:
                    if printlist:
                        print "In line %i, the word < %s > was not found (no suggested correction)" % (i, doc_word)
                    unknown_word_count += 1
                elif suggestion[0]!=doc_word:
                    if printlist:
                        print "In line %i, %s: suggested correction is < %s >" % (i, doc_word, suggestion[0])
                    corrected_word_count += 1
        
    print "-----"
    print "total words checked: %i" % doc_word_count
    print "total unknown words: %i" % unknown_word_count
    print "total potential errors found: %i" % corrected_word_count

    return

## main

import time

if __name__ == "__main__":
    
    print "Please wait..."
    time.sleep(2)
    start_time = time.time()
    create_dictionary("big.txt")
    run_time = time.time() - start_time
    print '-----'
    print '%.2f seconds to run' % run_time
    print '-----'

    print " "
    print "Word correction"
    print "---------------"
    
    while True:
        word_in = raw_input('Enter your input (or enter to exit): ')
        if len(word_in)==0:
            print "goodbye"
            break
        start_time = time.time()
        print get_suggestions(word_in)
        run_time = time.time() - start_time
        print '-----'
        print '%.6f seconds to run' % run_time
        print '-----'
        print " "