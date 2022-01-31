from DskDb import *

fileStream=open("file.dskdb","rb") #Open file in binary read mode
data=diskDb.read(fileStream) #This will move the file pointer to the end of the data! Use fileStream.seek(0) before reading again
print(data)