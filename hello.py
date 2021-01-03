

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



# creates a copy of the input .docx file into a .txt file and returns contents as a single string
def initMe(initalFileName):
  # create a new file to work on:
  newFileName = initalFileName[:-5] + ".txt"
  originalContent = docx2txt.process(initalFileName)
  newFileObject = open(newFileName, "w")
  # copy over to the new file name:
  newFileObject.write(originalContent)
  print("init done");
  time.sleep(5)
  newFileObject.close();

# Gather our code in a main() function
def main():
  fileName = sys.argv[1]
  # fileName = "C:\Users\mkrit\OneDrive - National University of Singapore\a&r\lingus\temp\PoSTrialText.docx"
  initMe(fileName)
  time.sleep(5)


    # read a file:

    # using docx2txt
    

    # print (type(intermediateFile))
    # fileopen functions:
    # f = open("D:\\myfiles\welcome.txt", "r")
    # fileObject = open(fileName, "r")
    # print(fileObject.read())


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
  main()