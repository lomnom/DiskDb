# DiskDb, a non-bloat general data storage format
## Usage
### Bash shell
#### Non-interactive
Use `readdb.py input.dskdb output.yaml` to read a diskdb, and `writedb.py input.yaml output.dskdb ` to write to a diskdb
#### Interactive
Run `editdb toEdit.dskdb` to interactively edit your diskdb in nano, as yaml. Save the file to commit it to the diskdb.
### Python
#### Basic usage
1. Add `DskDb.py` to the same folder as the python script that you want to use diskdb with
2. Add this to the start of your python script to import diskdb
```py
from DskDb import *
```
3. Read from diskdbs with
```py
...
fileStream=open("file.dskdb","rb") #Open file in binary read mode
data=diskDb.read(fileStream) #This will move the file pointer to the end of the data! Use fileStream.seek(0) before reading again
...
```
4. Write to diskdbs with
```py
data={"Message":"This supporrts almost all python builtins, eg. str, list, bool, and bytes!"}
fileStream=open("file.dskdb","wb") #Open file in binary write mode
diskDb.store(data,fileStream)
```
#### Implementing your own storable
```py
class Human:
	def __init__(self,name: str, age: int, sex: str):
		self.name=name
		assert(age>0)
		self.age=age
		assert(sex=='m' or sex=='f')
		self.sex=sex

	def __str__(self): #Print the human
		return f"{self.name}, {self.sex}{self.age}"

storeHumans=Storable(Human,b'h')
diskDb.addStorable(storeHumans) # Register the specification

#iTb is int to bytes
@storeHumans.encoder
def encodeHuman(self,data): #data is the Human object
	ageSex=data.age if data.sex=='m' else -data.age #store sex in sign bit
	encodedData=iTb(data.age,size=1)+self.spec.encode(data.name)
	return self.header+encodedData #you have to add the header in front of the data

#bTi is bytes to int
@storeHumans.decoder
def decodeHuman(self,file): # file is a stream seeked to the position with data returned from encodeHuman, without the header.
	ageSex=bTi(file.read(1))
	age=abs(ageSex)
	sex='m' if age>0 else 'f'
	name=self.spec.decode(file) #decode one object from the stream (our name in this case)
	return Human(name,age,sex)

#Lets test it!
fileStream=open("Human.dskdb","wb")
diskDb.store(Human("lomnom",69,'f'),fileStream)
```
#### Im too lazy to write the rest, try reading the source code ;)
