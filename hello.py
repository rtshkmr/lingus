

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

# tag validator:
def isValidTag(tag): 
  return tag != "." 

# Gather our code in a main() function
def main():
  # note that the input file has to be in the same project directory
  initialFileName = sys.argv[1]
  newFileName = "workspace_" + initialFileName[:-5] + ".txt"
  contents = initMe(initialFileName, newFileName)
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
      if(isValidTag(tag)):
        print("iteration # %s with the word %s gives the word %s and has the tag %s" %(i, term, word, tag))
        words.append(word)
        tags.append(tag)
  outputFile(words, tags)
  print(words)
  print(tags)
  # print(contents)
  # print(workingFileObject.read())

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
  main()