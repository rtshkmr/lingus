

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



# creates a copy of the input .docx file into a .txt file and returns contents as an opened FileObject
def initMe(initialFileName, newFileName):
  # create a new file to work on:
  
  originalContent = docx2txt.process(initialFileName)
  newFileObject = open(newFileName, "w")
  # copy over to the new file name:
  newFileObject.write(originalContent)
  print("init done");
  return originalContent

# Gather our code in a main() function
def main():
  # note that the input file has to be in the same project directory
  initialFileName = sys.argv[1]
  newFileName = "workspace_" + initialFileName[:-5] + ".txt"
  contents = initMe(initialFileName, newFileName)
  print(contents)
  # print(workingFileObject.read())

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
  main()