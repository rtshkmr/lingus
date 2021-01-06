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


Written by: Alyssa Nah Xiao Ting and Ritesh Kumar
 ============================================== """
import sys
import docx2txt
import os, signal
import logging
import nltk
import spacy

# sp = spacy.load('en_core_web_sm')

logger = logging.getLogger("logger")
# logger.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# define constants here
OUTPUT_FILE_NAME = "./output"
THRESHOLD = 1
NUMBER_OF_UNCERTAINTIES = None




def main():
    # note that the input file has to be in the same project directory
    sourceFileName = sys.argv[1]
    workspaceFileName = "workspace_" + sourceFileName[:-5] + ".txt"
    contents = init(sourceFileName, workspaceFileName)
    finalWords, finalTags, stats = checkPOS(contents)
    writeToOutputFile(finalWords, finalTags)
    print(endingGreeting + stats)

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
        logger.debug("workspace file exists, shall read from it")
        workspaceContent = open(workspaceFileName, "r").read()
        logger.debug(
            ">>> the file exists and here's the contents \n ================================ \n"
            + workspaceContent
            + "\n ================================ \n"
            + "\n\n\n"
        )
    else:
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
    words, tags = [], {"original": [], "nltk": []}
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
    # ===============================================================================
    return [words, tags]


# correctly assigns the POS to each word, returns a valid list of lists: [words, tags] where both words and tags are a list
def checkPOS(contents):
    words, tags = preprocessTerms(contents)
    originalTags, nltkTags = tags["original"], tags["nltk"]
    print(
        f"SEE HERE: \n\n \t =========== original tags: ============= \n {originalTags} \n\n \t =========== nltk tags: ============= \n {nltkTags}"
    )
    scores = caclulateScore(tags)
    uncertainTagIndices = detectDiscrepencies(scores, THRESHOLD)
    numberOfUncertainties = len(uncertainTagIndices)
    finalisedTags = []
    for idx in range(
        len(words)
    ):  # asks for human to check only for the uncertain indices
        currentTag = originalTags[idx]
        if idx in uncertainTagIndices:
            wordsBefore, wordsAfter = 0 if idx < 10 else (idx - 10), len(words) if idx >= len(words) - 10 else (idx + 10)
            currentTerm = "" + words[idx] + "_" + currentTag
            # generates some reference text to help determine the correct tag for that word:
            #==================================================================================
            referenceText = "\n\t\t Here's the nearby text for reference:\n\n ================================ \n\t\t"
            for x in range(wordsBefore, wordsAfter):
                referenceText += (("{" + words[x] + "}") if idx == x else words[x]) + " "
            #==================================================================================
            finalisedTag = determineCorrectTag(currentTerm, referenceText)
            finalisedTags.append(finalisedTag)
        else:
            finalisedTags.append(currentTag)

    stats = f"\n\nThe human was involved for {str(numberOfUncertainties)} times for {len(words)} valid terms."
    return (words, finalisedTags, stats)


# determines which scores are too low, and judges that as a discrepency
# returns a list of indices respective to the original array to reflect what needs to be prompted to human
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
        if not isValidTag:
            showHelp()
            userInput = input("Enter valid tag:").upper()
            if userInput not in PosDictionary.keys():
                continue
            else:
                tag = PosDictionary.get(userInput)
    return tag

# input: dictionary of generated Tags
#  returns a list of scores
# TODO: make this generalised once we use more than 1 reference models
def caclulateScore(generatedTags):
    stanfordTags, nltkTags = generatedTags["original"], generatedTags["nltk"]
    assert len(stanfordTags) == len(nltkTags)
    scores = []
    for idx in range(len(stanfordTags)):
        score = 0
        if stanfordTags[idx] == nltkTags[idx]:
            score = 1  # TODO: do the weighted calculation i(wnith spacy etc)   the next update to this function
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
    submissionFile = open(OUTPUT_FILE_NAME + "_submission" , "a+")
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
    while(rightPtr >= leftPtr):
        leftKey, leftValue = keys[leftPtr], values[leftPtr]
        rightKey, rightValue = keys[rightPtr], values[rightPtr]
        if leftPtr != rightPtr:
            if rightPtr >= 25:
                message += (f"{leftKey}: {leftValue} \t\t\t {rightKey}: {rightValue} \n")  # this is just to prettify the printing, purely aesthetic
            else: 
                message += (f"{leftKey}: {leftValue} \t\t {rightKey}: {rightValue} \n") 
        else: 
            message += (f"{rightKey}: {rightValue} \n") 
        rightPtr -= 1; leftPtr += 1
    message += line
    print(message)


endingGreeting = f"""
================================================================================================
8888888                                                           888                               
  888                                                             888                               
  888                                                             888                               
  888        8888b.  88888b.d88b.      .d8888b   .d88b.       .d88888  .d88b.  88888b.   .d88b.     
  888           "88b 888 "888 "88b     88K      d88""88b     d88" 888 d88""88b 888 "88b d8P  Y8b    
  888       .d888888 888  888  888     "Y8888b. 888  888     888  888 888  888 888  888 88888888    
  888       888  888 888  888  888          X88 Y88..88P     Y88b 888 Y88..88P 888  888 Y8b.    d8b 
8888888     "Y888888 888  888  888      88888P'  "Y88P"       "Y88888  "Y88P"  888  888  "Y8888 Y8P 
================================================================================================

"""

if __name__ == "__main__":
    main()
