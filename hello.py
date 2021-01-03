

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



# creates a copy of the input .docx file into a .txt file and returns contents as an opened FileObject
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


# 4 --> CC

# tag validator:
def isTag(tag): 
  # TODO: add in a dict of all the possible POS. if the tag is not in this dict, then return false
  POSArray=["CC"]
  return tag != "." 



# each word will prompt an input to ask us if its in the correct category. if wrong, then asks helper to reassign the tag to a valid tag
# returns a list: [correctWords, correctTags]
def promptHuman(initialWords, initialTags):
  correctWords, correctTags = [], []
  size = len(initialWords)

  # for i in range(size):
  #   # check if it's a valid word -- tag assignment [goes through every word]
  #   isValid = "Y" == input("Is this valid? \[ %s + %s \] \n \t type Y or N ", initialWords[i], initialTags[i]).capitalize
  #   # if not, then
  #   if not isValid:
  #     # ask the human what is valid out of the
  #     # they enter valid tag 
  #     # we use isTag to check if its valid
  #   else: 
  #     correctWords.append(initialWords[i])
  #     correctTags.append(initialTags[i])

  return [correctWords, correctTags]

# correctly assigning the POS to each word, returns a valid list of lists: [words, tags] in a list
def checkPOS(contents):
  splitContents = contents.split(" ")
  size = len(splitContents)
  words = [size]
  tags = [size]
  print("XXX ", )
  for i in range(size):
    term = splitContents[i]
    if "_" in term:   
      splitTerm = term.split("_")
      word, tag  = splitTerm[0], splitTerm[1]
      # add in a check the tag should be valid
      if(isTag(tag)):
        print("iteration #%s with the term %s gives the word %s and has the tag %s" %(i, term, word, tag))
        words.append(word)
        tags.append(tag)
  return promptHuman(words, tags)
  # TODO: call a helper that shall make the human check if the current tag is logically correct or not, 
  # each word will prompt an input to ask us if its in the correct category. if wrong, then asks helper to reassign the tag to a valid tag


# Gather our code in a main() function
def main():
  # note that the input file has to be in the same project directory
  initialFileName = sys.argv[1]
  newFileName = "workspace_" + initialFileName[:-5] + ".txt"
  contents = initMe(initialFileName, newFileName)
  arr = checkPOS(contents)
  words, tags = arr[0], arr[1]
  outputFile(words, tags)





# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
  main()