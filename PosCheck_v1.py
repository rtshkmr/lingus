""" ==========================================
This is a convenience program written to improve our 
manual checking of PoS tagging done. This should serve
as a useful boilerplate to add in more functionality
as a user so wishes. 

Next versions will cross check existing POS tagging libs
and ask the human only if there are discrepancies.

Written by: Alyssa Nah Xiao Ting and Ritesh Kumar
 =============================================="""
import sys
import docx2txt
import os, signal
import logging

OUTPUT_FILE_NAME = "./jizz"

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


logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def main():
    # note that the input file has to be in the same project directory
    sourceFileName = sys.argv[1]
    workspaceFileName = "workspace_" + sourceFileName[:-5] + ".txt"
    contents = init(sourceFileName, workspaceFileName)
    finalWords, finalTags = checkPOS(contents)
    writeToOutputFile(finalWords, finalTags)


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


# correctly assigning the POS to each word, returns a valid list of lists: [words, tags] in a list
def checkPOS(contents):
    splitContents = contents.split(" ")
    size = len(splitContents)
    words, tags = [size], [size]
    for i in range(size):  # iters thru term where term is <word>_<tag>
        term = splitContents[i]  # word_tag
        if "_" in term:
            splitTerm = term.split("_")
            word, tag = splitTerm[0], splitTerm[1]
            # add in a check the tag should be valid
            if validateTag(tag):
                logger.debug(
                    "iteration #%s with the term %s gives the word %s and has the tag %s"
                    % (i, term, word, tag)
                )
                words.append(word)
                tags.append(tag)
    return promptHuman(words, tags)


# cleans up the program upon a signal interruption by
# 1: appending checkedWords and checkedTags to the output file
# 2: overwriting the workspace file with the uncheckedWords and uncheckedTags
def cleanup(checkedWords, checkedTags, uncheckedWords, uncheckedTags):
    writeToOutputFile(checkedWords, checkedTags)
    remainingContent = ""
    for i in range(len(uncheckedWords)):
        remainingContent += uncheckedWords[i] + "_" + uncheckedTags[i] + " "
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


# appends to output file
def writeToOutputFile(words, tags):
    outputFile = open(OUTPUT_FILE_NAME, "a+")
    size = len(words)
    string = ""
    for i in range(size):
        word, tag = words[i], tags[i]
        entry = "[" + str(word) + "_" + str(tag) + "]"
        string += entry + "\n"
    outputFile.write(string)


# promts a human to check if the current associated tag to a word is correct and asks for correct input otherwise
# returns a list: [correctWords, correctTags]
# TODO: improve prompting by :
#   1. give users a list of possible tags they can access by entering their repsective key number as per the dictionary we have
#   2. Maybe do some control flow e.g. step 1 user chooses noun, then step 2: what kinda noun, proper?...
def promptHuman(initialWords, initialTags):
    size = len(initialWords)
    checkedWords, checkedTags = [size], [size]
    for i in range(size):
        newTag = initialTags[i]  # first initial tag from array
        isValidTag = False
        while (
            not isValidTag
        ):  # keep prompting for that word until user agrees and enters Y for yes
            prompt = f"Is this valid? \n \t [ {initialWords[i]} \n\t --------- \n\t       {newTag} ] \n \t type Y or N "
            userInput = ""
            try:
                userInput = (input(prompt)).upper()
            except KeyboardInterrupt:  # this allows us to pause the process by pressing CTRL+C
                logger.debug("DETECTED CTRL C")
                uncheckedWords, uncheckedTags = initialWords[i:], initialTags[i:]
                cleanup(checkedWords, checkedTags, uncheckedWords, uncheckedTags)
            isValidTag = (userInput == "Y") and validateTag(newTag)
            if not isValidTag:
                newTag = input("Enter valid tag:").upper()
            else:
                checkedWords.append(initialWords[i])
                checkedTags.append(newTag)
                break
    return [checkedWords, checkedTags]


def validateTag(tag):
    return tag in PosDictionary.values()


if __name__ == "__main__":
    main()
