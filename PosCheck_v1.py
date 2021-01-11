""" ==========================================
This is a convenience program written to improve our 
manual checking of PoS tagging done. This should serve
as a useful boilerplate to add in more functionality
as a user so wishes. 

Next versions will cross check existing POS tagging libs
and ask the human only if there are discrepancies.

possible issues to face: 
1. the workspace file is overwritten to reflect that most 
   status. i.e. the unchecked terms. but the overwriting
   does not preserve the original whitespace in the source
   document. (actually we never ever preserve the whitespace
   from the source document)

Questions:
1. Input file related queries:
    a. How come there are duplicate words in the input file?
    b. How come some words are erroneously joined "generalhospital"?

Todos:
1. DoubleCheck logging (Ritesh to get up to speed with this)
2. Fix the duplicated words problem
   - see alyssa's use of the enchant dictionary to filter through for words not in a dictionary
3.





Written by: Alyssa Nah Xiao Ting and Ritesh Kumar
 ============================================== """
import sys
import docx2txt
import os, signal
import logging
import nltk
import spacy
from pyfiglet import Figlet

# sp = spacy.load('en_core_web_sm')

logger = logging.getLogger("logger")
# logger.setLevel(logging.DEBUG)
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

logging.basicConfig(filename="logging_output.txt",
                    filemode='a+',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

# define constants here
OUTPUT_FILE_NAME = "./output"
THRESHOLD = 1.5
NUMBER_OF_UNCERTAINTIES = None
f = Figlet(font="colossal")
# TODO: import this wordlist from somewhere in the internet. there should be singlish wordlists
SinglishWords = ["LA", "LAH", "LOR", "AH", "MEH", "LEH", "HOR"]
PseudoSinglishWords = ["ONE", "WHAT"]
tagsChanged = []


def main():
    logger.debug("\n\n\n>>>>>>>>>>>>>>>>>>>>>> Running Script Now <<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n\n\n")
    # note that the input file has to be in the same project directory
    sourceFileName = sys.argv[1]
    workspaceFileName = "workspace_" + sourceFileName[:-5] + ".txt"
    contents = init(sourceFileName, workspaceFileName)
    finalWords, finalTags, stats = checkPOS(contents)
    writeToOutputFile(finalWords, finalTags)
    print(endingGreeting + stats)
    logger.debug("\n\n\n>>>>>>>>>>>>>>>>>>>>>> Done Running script <<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n\n\n")
    # note that the input file has to be in the same project directory

# returns an array containing tagging done by spacy
def generateSpacyTags(words):
    prose = ""
    for word in words:
        prose += word + " "
    tagger = spacy.load("en_core_web_sm")
    doc = tagger(prose)
    tags = []
    for token in doc:
        tags.append(token.tag_)
    return tags



# returns an array containing NLTK tags
def generateNLTKtags(words):
    nltkOutput = nltk.pos_tag(words)
    nltkTags = []
    for term in nltkOutput:
        nltkTags.append(term[1])  # nb: nltk output is an array of tuples that's why nltkOutput: [(<word>_<tag>), etc..]
    return nltkTags


# returns contents from the workspace if workspace aldy exists, else copies from source to new workspace:
def init(sourceFileName, workspaceFileName):
    workspaceContent = ""
    if os.path.isfile(workspaceFileName):
        # logger.debug("workspace file exists, shall read from it")
        workspaceContent = open(workspaceFileName, "r").read()
        sourceContent = docx2txt.process(sourceFileName)
        workspaceContent = writeToWorkspace(sourceContent, workspaceFileName)
        logger.debug(">>> init done")
    return workspaceContent


# preprocesses the single string of contents and returns the following list: [words, tags]
#   where words is a list of words [w1, w2, w3,...]
#   tags is a dictionary that maps a tagger (e.g. stanford, nltk...) to a list of tags associated to the words list
#       e.g. tags = {
#                   "original" : [t1, t2, t3,...],
#                   ...
#                   }
def preprocessTerms(contents):
    splitContents = contents.split(" ")
    size = len(splitContents)
    words, tags = [], {"original": []}
    # ============== populate the words array and the tags dict =====================
    for i in range(size):  # iters thru term where term is <word>_<tag>
        term = splitContents[i]  # word_tag
        if "_" in term:
            splitTerm = term.split("_")
            word, originalTag = splitTerm[0], splitTerm[1]
            # add in a check the tag should be valid
            if validateTag(originalTag):
                # logger.debug(
                #     "iteration #%s with the term %s gives the word %s and has the tag %s"
                #     % (i, term, word, originalTag)
                # )
                # separated words and tags into different arrays
                words.append(word)
                tags["original"].append(originalTag)
    tags["nltk"] = generateNLTKtags(words)
    tags["spacy"] = generateSpacyTags(words)
    # ===============================================================================
    return [words, tags]


# auto tags the confirmed singlish words and retuns the updated tags and updatedUncertainTagIndices
def autoTagWords(scores, words, currentTags, currentUncertainTagIndices):
    updatedTags, updatedUncertainTagIndices = [], currentUncertainTagIndices
    print(f" SEE HERE scores length: {len(scores)}, words length: {len(words)},tags length: {len(currentTags)}")
    assert len(scores) == len(words) == len(currentTags)
    for idx in range(len(words)):
        word, score, updatedTag = words[idx], scores[idx], currentTags[idx]
        # autoTagsSinglish words:
        if (
                word in SinglishWords and score == -1):  # just being extra safe, could have just iterated thorugh scores without looking thru any of the words actually TODO: consider optimising this
            # autotag
            updatedTag = "SFP"
            # remove from uncertainTagIndices if the idx has been flagged
            if idx in currentUncertainTagIndices:
                updatedUncertainTagIndices.remove(idx)
        updatedTags.append(updatedTag)
    return words, updatedTags, updatedUncertainTagIndices


# correctly assigns the POS to each word, returns a valid list of lists: [words, tags] where both words and tags are a list
def checkPOS(contents):
    words, tagsDict = preprocessTerms(contents)
    assert (len(words) == len(tagsDict["original"]) == len(
        tagsDict["nltk"]) == len(tagsDict["spacy"])), "words and tag arrays are not the same length in checkPOS()"
    originalTags, nltkTags, spacyTags = tagsDict["original"], tagsDict["nltk"], tagsDict["spacy"]
    print(
        f"SEE HERE: \n\n \t =========== original tags: ============= \n {originalTags} \n\n \t =========== nltk tags: ============= \n {nltkTags} \n\n \t =========== spacy tags: ============= \n {spacyTags}"
    )
    scores = calculateScores(words, tagsDict)
    logger.info(f"\n Scores have been calculated. \n {scores} ")
    indices = detectDiscrepencies(scores, THRESHOLD)
    words, updatedTags, uncertainTagIndices = autoTagWords(scores, words, originalTags, indices)
    numberOfUncertainties = len(uncertainTagIndices)
    logger.info(f" THRESHOLD VALUE of {THRESHOLD} gives us {numberOfUncertainties} uncertainties that require human assistance out of {len(words)}. \n {100 * (numberOfUncertainties / len(words))} % of tagging done by Stanford Tagger needs to be reviewed by a human. ")
    finalisedTags = []
    for idx in range(
            len(words)
    ):  # asks for human to check only for the uncertain indices
        currentTag = updatedTags[idx]
        if idx in uncertainTagIndices:
            wordsBefore, wordsAfter = 0 if idx < 10 else (idx - 10), len(words) if idx >= len(words) - 10 else (
                        idx + 10)
            currentTerm = "" + words[idx] + "_" + currentTag
            # generates some reference text to help determine the correct tag for that word:
            # ==================================================================================
            referenceText = "\n\t\t Here's the nearby text for reference:\n\n ================================ \n\t\t"
            for x in range(wordsBefore, wordsAfter):
                referenceText += (("{" + words[x] + "}") if idx == x else words[x]) + " "
            # ==================================================================================
            finalisedTag = determineCorrectTag(currentTerm, referenceText)
            finalisedTags.append(finalisedTag)
        else:
            finalisedTags.append(currentTag)

    # print("**** THIS IS FINALISED TAGS ", finalisedTags)
    # print("**** THESE ARE CHANGED TAGS ", tagsChanged)
    stats = f"\n\nThe human was involved for {str(numberOfUncertainties)} times for {len(words)} valid terms."
    return (words, finalisedTags, stats)


# determines which scores are too low, and judges that as a discrepency
# returns a list of indices respective to the original array to reflect what needs to be prompted to human
# scores: the word list: [w1, w2, ...] will have associated scores for each word as a list: [s1, s2...]
# threshold: a minimum score for a single word. 
def detectDiscrepencies(scores, threshold):
    discrepencies = []
    for idx in range(len(scores)):
        score = scores[idx]
        if score < threshold:
            discrepencies.append(idx)
    return discrepencies  # list of index for humanPrompt to execute on


# asks human what the correct tag should be(<word>_<tag>) because a discrepancy has been found
# returns the correct tag for that particular word
def determineCorrectTag(term, referenceText):
    # referenceText = "\n\t\t Here's the nearby text for reference:\n\n ================================ \n\t\t"
    # for word in neighbouringWords:
    #     referenceText += word + " "
    print(referenceText)
    splitTerm = term.split("_")
    word, tag = splitTerm
    isValidTag = False
    while not isValidTag:
        prompt = f"Is this valid? \n \t [ {word} \n\t --------- \n\t       {tag} ] \n \t type Y or N "
        userInput = ""
        try:
            userInput = (input(prompt)).upper()
        except KeyboardInterrupt:
            # TODO: figure out how to do the pausing later
            logger.debug("DETECTED CTRL C")
        isValidTag = (userInput == "Y") and validateTag(tag)
        logging.info('Checked for the word {' + word + '} and the tag {' + tag + '}')
        if not isValidTag:
            showHelp()
            userInput = input("Enter valid tag:").upper()
            logging.info('Tag entered: ' + userInput + ' for the word ' + word)
            if userInput not in PosDictionary.keys():
                continue
            else:
                tag = PosDictionary.get(userInput)
        tagsChanged.append(tag)
    return tag


# compares tag arrs and gives a weighted sum of their matches based on their published frequencies.
def calculateWeightedSum(tagsDict, idx):
    stanfordTag = tagsDict["original"][idx]
    nltkTag = tagsDict["nltk"][idx]
    spacyTag = tagsDict["spacy"][idx]
    c0 = 1 * (PublishedAccuracies["stanford"])
    c1 = (1 if stanfordTag == nltkTag else 0) * (PublishedAccuracies["nltk"])
    c2 = (1 if stanfordTag == spacyTag else 0) * (PublishedAccuracies["spacy"])
    return c0 + c1 + c2


# input: dictionary of generated Tags
#  returns a list of scores
# if it's a confirmed to be a singlish wrod, then we set the score as -1
# if it's a pseudoSinglish word, e.g. "one" then we set the score to be 0

# TODO: make this generalised once we use more than 1 reference models
def calculateScores(words, generatedTags):
    stanfordTags, nltkTags, spacyTags = generatedTags["original"], generatedTags["nltk"], generatedTags["spacy"]
    size = len(stanfordTags)
    assert size == len(nltkTags) == len(spacyTags)
    scores = []
    for idx in range(size):
        word = words[idx].upper()
        if word in SinglishWords:
            score = -1  # looking at scores array, we can say that - 1 means safe to autocheck without asking the human
        elif word in PseudoSinglishWords:
            score = 0  # means there's definitely gonna be some discrepancy
        else: # actual weighted score calculation
            # here, my word isn't singlish word nor is it a potentially singlish word. it's proper english.
            # i have tagged them using 3 models: original, nltk, spacy
            # generatedTags[nltkTags][x] and generatedTags[spacy][x] they all refer to the same word that has been tagged.
            # so, to calculate weighted sum for the xth word, we just need to pass in the generated tags and the index
            # of the word that we are looking at.
            score = calculateWeightedSum(generatedTags, idx)
        scores.append(score)
    return scores


# cleans up the program upon a signal interruption by
# 1: appending checkedWords and checkedTags to the output file
# 2: overwriting the workspace file with the uncheckedWords and uncheckedTags
def cleanup(checkedWords, checkedTags, uncheckedWords, uncheckedTags):
    writeToOutputFile(checkedWords, checkedTags)
    remainingContent = ""
    for i in range(len(uncheckedWords)):
        remainingContent += str(uncheckedWords[i]) + "_" + str(uncheckedTags[i]) + " "
    writeToWorkspace(
        remainingContent, workspaceFileName="workspace_PoSTrialText.txt"
    )  # TODO: make everythign into a class so that can set the filenames as a class level variable after init
    os.kill(os.getpid(), signal.SIGINT)


# writes content to a workspace file. Intentionally overwrites if there's an existing file:
def writeToWorkspace(content, workspaceFileName):
    workspaceFile = open(workspaceFileName, "w")
    # copy over to the new file name:
    workspaceFile.write(content)
    workspaceFile.close()
    logger.debug(">>> wrote to Workspace")
    return content


# appends to non-existing / pre-existing output file
def writeToOutputFile(words, tags):
    outputFile = open(OUTPUT_FILE_NAME, "a+")
    submissionFile = open(OUTPUT_FILE_NAME + "_submission", "a+")
    size = len(words)
    outputString, submissionString = "\n===================== STARTING LINE =============================\n", "\n"
    for i in range(size):
        word, tag = words[i], tags[i]
        outputEntry, submissionEntry = "[" + str(word) + "_" + str(tag) + "]", str(word) + "_" + str(tag) + " "
        outputString += outputEntry + "\n"
        submissionString += submissionEntry
    outputFile.write(outputString)
    submissionFile.write(submissionString)


def validateTag(tag):
    return tag in PosDictionary.values()


# tagging accuracies of models when input is standard English
PublishedAccuracies = {
    "stanford" : 0.9697, # https://tinyurl.com/stanfordTagger-accuracy
    "nltk": 0.94,
    "spacy": 0.5
}


PosDictionary = {}
PosDictionary["1"] = "CC"
PosDictionary["2"] = "CD"
PosDictionary["3"] = "DT"
PosDictionary["4"] = "EX"
PosDictionary["5"] = "FW"
PosDictionary["6"] = "IN"
PosDictionary["7"] = "JJ"
PosDictionary["8"] = "JJR"
PosDictionary["9"] = "JJS"
PosDictionary["10"] = "LS"
PosDictionary["11"] = "MD"
PosDictionary["12"] = "NN"
PosDictionary["13"] = "NNS"
PosDictionary["14"] = "NNP"
PosDictionary["15"] = "NNPS"
PosDictionary["16"] = "PDT"
PosDictionary["17"] = "POS"
PosDictionary["18"] = "PRP"
PosDictionary["19"] = "PRP$"
PosDictionary["20"] = "RB"
PosDictionary["21"] = "RBR"
PosDictionary["22"] = "RBS"
PosDictionary["23"] = "RP"
PosDictionary["24"] = "SYM"
PosDictionary["25"] = "TO"
PosDictionary["26"] = "UH"
PosDictionary["27"] = "VB"
PosDictionary["28"] = "VBD"
PosDictionary["29"] = "VBG"
PosDictionary["30"] = "VBN"
PosDictionary["31"] = "VBP"
PosDictionary["32"] = "VBZ"
PosDictionary["33"] = "WDT"
PosDictionary["34"] = "WP"
PosDictionary["35"] = "WP$"
PosDictionary["36"] = "WRB"
PosDictionary["37"] = "SFP"


def showHelp():
    line = "___________________________________________________\n"
    keys, values = list(PosDictionary.keys()), list(PosDictionary.values())
    message = "\n----- {enter number representing the tag} -------- \n" + line
    leftPtr, rightPtr = 0, len(keys) - 1
    while (rightPtr >= leftPtr):
        leftKey, leftValue = keys[leftPtr], values[leftPtr]
        rightKey, rightValue = keys[rightPtr], values[rightPtr]
        if leftPtr != rightPtr:
            if rightPtr >= 25:
                message += (
                    f"{leftKey}: {leftValue} \t\t\t {rightKey}: {rightValue} \n")  # this is just to prettify the printing, purely aesthetic
            else:
                message += (f"{leftKey}: {leftValue} \t\t {rightKey}: {rightValue} \n")
        else:
            message += (f"{rightKey}: {rightValue} \n")
        rightPtr -= 1;
        leftPtr += 1
    message += line
    print(message)


# def outputLoggingFile(changedTags):


endingGreeting = f"""
================================================================================================ \n
{f.renderText("I am so done")}
 \n
================================================================================================

"""

if __name__ == "__main__":
    main()
