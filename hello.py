

# // pass the entire text in

# // extract into <word>_<tag> 

# // ask if <tag> is accurate


# 	// if not, select new tag. This requires like 2-3 levels of user inputs e.g. Noun? --> what kinda noun

#         // same for verb as well

# // have an 36 arrays of POS category

#***********************************
# import modules used here -- sys is a very standard one
import sys
import docx2txt
import time
import os


POSDictionary = {}
POSDictionary["1"] = "CC"
POSDictionary["2"] = "CD"
POSDictionary["3"] = "DT"
POSDictionary["4"] = "EX"
POSDictionary["5"] = "FW"
POSDictionary["6"] = "IN"
POSDictionary["7"] = "JJ"
POSDictionary["8"] = "JJR"
POSDictionary["9"] = "JJS"
POSDictionary["10"] = "LS"
POSDictionary["11"] = "MD"
POSDictionary["12"] = "NN"
POSDictionary["13"] = "NNS"
POSDictionary["14"] = "NNP"
POSDictionary["15"] = "NNPS"
POSDictionary["16"] = "PDT"
POSDictionary["17"] = "POS"
POSDictionary["18"] = "PRP"
POSDictionary["19"] = "PRP$"
POSDictionary["20"] = "RB"
POSDictionary["21"] = "RBR"
POSDictionary["22"] = "RBS"
POSDictionary["23"] = "RP"
POSDictionary["24"] = "SYM"
POSDictionary["25"] = "TO"
POSDictionary["26"] = "UH"
POSDictionary["27"] = "VB"
POSDictionary["28"] = "VBD"
POSDictionary["29"] = "VBG"
POSDictionary["30"] = "VBN"
POSDictionary["31"] = "VBP"
POSDictionary["32"] = "VBZ"
POSDictionary["33"] = "WDT"
POSDictionary["34"] = "WP"
POSDictionary["35"] = "WP$"
POSDictionary["36"] = "WRB"


# creates a copy of the input .docx file into a .txt file and returns contents as a single string
def initMe(initialFileName, newFileName):
  # create a new file to work on:
  originalContent = docx2txt.process(initialFileName)
  newFileObject = open(newFileName, "w")
  # copy over to the new file name:
  newFileObject.write(originalContent)
  print("init done");
  return originalContent

def outputFile(words, tags):
  newFileName = "./jizz"
  newFileObject = open(newFileName, "w")
  size = len(words)
  string = ""
  for i in range(size):
     word, tag = words[i], tags[i]
     string += str(word) + "---" + str(tag) + " \n"
  newFileObject.write(string)

# each word will prompt an input to ask us if its in the correct category. if wrong, then asks helper to reassign the tag to a valid tag
# returns a list: [correctWords, correctTags]
def promptHuman(initialWords, initialTags):
  size = len(initialWords)
  correctWords, correctTags = [size], [size]
  for i in range(size):
    newTag = initialTags[i] # first initial tag from array
    isValid = False
    while isValid == False: # keep prompting for that word until user agrees and enters Y for yes
      prompt = f"Is this valid? [ {initialWords[i]}        {newTag} ] \n \t type Y or N "
      userInput = (input(prompt)).upper()
      isValid = (("Y" == userInput) and validateTag(newTag))
      if  isValid == False:
        newTag = input ("Enter valid tag:").upper()
      else:
        correctWords.append(initialWords[i])
        correctTags.append(newTag)
        break

  return [correctWords, correctTags]

def validateTag(tag) :
   return tag in POSDictionary.values()

# correctly assigning the POS to each word, returns a valid list of lists: [words, tags] in a list
def checkPOS(contents, POSDictionary):
  splitContents = contents.split(" ") 
  size = len(splitContents)
  words = [size]
  tags = [size]
  print("XXX ", )
  for i in range(size): # iters thru term where term is <word>_<tag>
    term = splitContents[i] # word_tag
    if "_" in term:   
      splitTerm = term.split("_")
      word, tag  = splitTerm[0], splitTerm[1]
      # add in a check the tag should be valid
      if(validateTag(tag)):
        print("iteration #%s with the term %s gives the word %s and has the tag %s" %(i, term, word, tag))
        words.append(word)
        tags.append(tag)
  return promptHuman(words, tags)
  # TODO: call a helper that shall make the human check if the current tag is logically correct or not, 
  # each word will prompt an input to ask us if its in the correct category. if wrong, then asks helper to reassign the tag to a valid tag


# Gather our code in a main() function
def main():
  # TODO: add in a dict of all the possible POS. if the tag is not in this dict, then return false
  
  # note that the input file has to be in the same project directory
  initialFileName = sys.argv[1]
  newFileName = "workspace_" + initialFileName[:-5] + ".txt"
  contents = initMe(initialFileName, newFileName)
  arr = checkPOS(contents, POSDictionary)
  words, tags = arr[0], arr[1]
  outputFile(words, tags)





# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
  main()