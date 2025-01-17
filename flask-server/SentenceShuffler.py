"""
● We want to research the processes and challenges that will be associated with
translating the ASL sentences into English once we have identified the individual words
● The goal is to identify libraries/code that will be useful in parsing and reorganizing
sentences
● Ideally we will make a prototype for this translation that can handle some simple
sentences, but this will depend on how many libraries already exist and how helpful they
will turn out to be.


NLTK (python library) seems to be an interesting option for this can tokenize sentences

Seems very powerful/possibly overkill for what we are trying to do 

it has a lot of different uses, the vast majority seem useless to us but this might be powerful
enough to just eat this project alive, which would be very PogChamp

Ok so it seems that this is EVEN COOLER than I initially realized, the tagging function is actually context dependent, so it will figure
out if a word is actually the verb of the sentence. an example of this is the sentence "I wore my running shoes this morning", it correctly 
identifies that "running" is not the verb, but it's instead a part of "running shoes". I have a very strong suspicion that this won't work on
a ASL formatted sentence but it is cool to keep in mind

The translate function might be useful for moving words around within the sentence

list of tags and their meaning https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
Examples of tags https://stackoverflow.com/questions/15388831/what-are-all-possible-pos-tags-of-nltk

Assuming we can kinda identify the POS of the words in the sentence, how do we reconstruct the sentence to match what we want
I imagine the steps of this process are going to be
1. Reorder the words in the sentence from TOPIC-COMMENT -> SUBJECT-VERB-OBJECT without adding words (Tomorrow library I go -> I go library tomorrow)
2. Identify the tense of the sentence (find time words, look for non-word queues) and conjugate the verb (I go library tomorrow -> I will go library tomorrow)
3. Add supporting words to make the sentence make sense (I will go library tomorrow -> I will go to the library tomorrow) (I bet a lot of these will be homebrew/vibes)

ideas for easy/distinct words
school, I, you, we, tomorrow, name, my, have, yesterday, what, go, hello, car
"""
import ssl
import sys

import nltk

# for MAC users
# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context
# nltk.download('averaged_perceptron_tagger')
# nltk.download('punkt')


# for users not on MAC
# nltk.download('averaged_perceptron_tagger')
# nltk.download('punkt')


#We can do the first 2 test sentences and anything with a similar grammatical structure
# TEST_SENTENCES = ["yesterday school I go", "my name Mat yesterday", "your name what", "yesterday car I have", "yesterday my school I go"]
TimeWords = ["tomorrow", "yesterday", "today"]
knownVerbs = [["have", "will have", "had"], ["go", "will go", "went"], ["is", "will be", "was"]]

foundObject = False
Question=False
Tense = ""

def getTaggedSentence(tagged):
    sentence = ""
    for token in tagged:
        sentence+=token[0]
        sentence+=" "
    return sentence

    

#now that we have figured out each word's place in the sentence, reorder the words
def sortWords(token):
    global foundObject
    POS=token[1]
    if token[0] in TimeWords:
        global Tense
        if(token[0] == "tomorrow"):
            Tense = "future"
        if(token[0]=="yesterday"):
            Tense = "past"
        return 4
    if "VB" in POS:
        return 2
    if "NN" in POS or "PRP" in POS:
        if foundObject:
            return 1
        else:
            foundObject = True
            return 3
    if "W" in POS:
        Question=True
        return 1
    else :
        return 999

def combinePhrases(tagged):
    i = 0
    for token in tagged:
        if token[0]=="my" or token[0]=="your":#if we have a possesion word, we must ensure that it stays next to whatever word it is possessing
            nextToken = tagged[i+1]
            x=list(token)
            x[0]+= " "+nextToken[0]
            x[1]=nextToken[1]
            tagged[i]=tuple(x)
            del tagged[i+1]
        i+=1
    print(tagged)


#Conjugate the verb based on tense
def findVerbPlace(tagged):
    i = 0
    for token in tagged:
        if "VB" in token[1]:
            return i
        else:
            i+=1
    return 99


def findVerb(tagged):
    verbPlace = findVerbPlace(tagged)#find the verb in the sentence
    if(verbPlace==99):
        return knownVerbs[2]
    for verb in knownVerbs:#for each known verb
        for conjugated in verb:#and for each conjugation
            if tagged[verbPlace][0]==conjugated:#check 
                return verb


def conjugateSentence(tagged):
    verbPlace = findVerbPlace(tagged)
    foundVerb = []
    if(verbPlace==99):#if no verb is found in the sentence
        tagged.insert(1, ("is", "VBP"))#we assume in this case that the verb is 'is'
        foundVerb = knownVerbs[2]#the verb 'is'
        verbPlace=1
    else:
        foundVerb = findVerb(tagged)
        print("found verb: "+foundVerb[0])
    if(Tense=="future"):
        tagged[verbPlace]=(foundVerb[1], "VB")
    if(Tense=="past"):
        tagged[verbPlace]=(foundVerb[2], "VB")


def applyheuristics(tagged):
    verbPlace = findVerbPlace(tagged)
    verb = findVerb(tagged)
    if verb[0] =="go":
        tagged.insert(verbPlace+1, ("to", "TO"))


def convertToEnglish(phrase):
    tokens = nltk.word_tokenize(phrase)#seperates the sentence into words
    print(tokens)
    tagged = nltk.pos_tag(tokens)#identify the parts of speech of each word    
    print(getTaggedSentence(tagged))
    print("Step 1: sort the existing words")
    combinePhrases(tagged)
    tagged.sort(key=sortWords)
    print(getTaggedSentence(tagged))
    print("Step 2: conjugate the sentence")
    conjugateSentence(tagged)
    print(tagged)
    print(getTaggedSentence(tagged))
    print("Step 3: apply heuristics")
    applyheuristics(tagged)
    print(getTaggedSentence(tagged))
    finalSentence = getTaggedSentence(tagged)
    return finalSentence

# phrase_to_convert = 'tomorrow car I have'

# english = convertToEnglish(phrase_to_convert)
# print('English Result:', english)
