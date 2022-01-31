# headers are \0<type>

#structure is <header|(\0type header|type data)+>

class StoreSpec:
	class NoHeaderError(Exception):
		def __str__(self):
			return "Header not found in file! It may not be a DiskDb."

	class NoHeaderWarning(Exception):
		def __str__(self):
			return "Header not found in file! Run the call with force=True to confirm!"

	def __init__(self,header):
		assert(type(header)==bytes)
		self.header=header
		self.storables=[]
		self.headers={}
		self.types={}

	def addStorable(self,storable):
		storable.spec=self
		self.storables+=[storable]
		self.headers[storable.header]=storable
		self.types[storable.stored]=storable

	def store(self,data,file,force=False):
		header=file.read(len(self.header))
		if (not force) and header != self.header:
			raise self.NoHeaderWarning

		file.seek(0)
		file.write(self.header)
		file.write(self.encode(data)+b"\0\0")

	def encode(self,data):
		return self.types[type(data)].encode(data)

	def read(self,file):
		header=file.read(len(self.header))
		if header != self.header:
			raise self.NoHeaderError

		return self.decode(file)

	def decode(self,file):
		header=file.read(2)
		return self.headers[header].decode(file)

class Storable:
	def __init__(self,stored,header):
		assert(type(header)==bytes)
		self.stored=stored
		self.headerCh=header
		self.header=b'\0'+header

	def encoder(self,func):
		self._encode=func

	def encode(self,file):
		return self._encode(self,file)

	def decoder(self,func):
		self._decode=func

	def decode(self,file):
		return self._decode(self,file)

diskDb=StoreSpec(b"DiskDb, another shitty database format!")

# bytes <-> int
def iTb(number,size=8):
	return number.to_bytes(size,"big")

def bTi(data):
	return int.from_bytes(data,"big")

# Store integers
storeInt=Storable(int,b'i')
diskDb.addStorable(storeInt)

@storeInt.encoder
def encodeInt(self,number):
	return self.header+iTb(number)

@storeInt.decoder
def decodeInt(self,file):
	return bTi(file.read(8))

# Strings
storeStr=Storable(str,b's')
diskDb.addStorable(storeStr)

@storeStr.encoder
def encodeStr(self,text):
	strData=bytes(text.encode("UTF8"))
	header=self.header+iTb(len(strData))
	return header+strData

@storeStr.decoder
def decodeStr(self,file):
	length=bTi(file.read(8))
	strData=str(file.read(length),encoding="UTF8")
	return strData

# NoneType
storeNone=Storable(type(None),b'n')
diskDb.addStorable(storeNone)

@storeNone.encoder
def encodeNone(self,data):
	return self.header

@storeNone.decoder
def decodeNone(self,file):
	return None

# Boolean
storeBool=Storable(bool,b'b')
diskDb.addStorable(storeBool)

@storeBool.encoder
def encodeBool(self,data):
	return self.header+ (b'\1' if data else b'\0')

@storeBool.decoder
def decodeBool(self,file):
	return bool(file.read(1)[0])

# Lists 
storeList=Storable(list,b'l')
diskDb.addStorable(storeList)

@storeList.encoder
def encodeList(self,data):
	header=self.header+iTb(len(data))
	encodedData=b''
	for item in data:
		encodedData+=self.spec.encode(item)
	return header+encodedData

@storeList.decoder
def decodeList(self,file):
	length=bTi(file.read(8))
	result=[]
	for item in range(length):
		result+=[self.spec.decode(file)]
	return result

# Dictionaries
storeDict=Storable(dict,b'd')
diskDb.addStorable(storeDict)

@storeDict.encoder
def encodeDict(self,data):
	length=iTb(len(data))
	encodedData=b''
	for key in data:
		encodedData+=self.spec.encode(key)+self.spec.encode(data[key])
	return self.header+length+encodedData

@storeDict.decoder
def decodeDict(self,file):
	length=bTi(file.read(8))
	result={}
	for item in range(length):
		key=self.spec.decode(file)
		value=self.spec.decode(file)
		result[key]=value
	return result

# Bytes
storeBytes=Storable(bytes,b'B')
diskDb.addStorable(storeBytes)

@storeBytes.encoder
def encodeBytes(self,data):
	header=self.header+iTb(len(data))
	return header+data

@storeBytes.decoder
def decodeBytes(self,file):
	length=bTi(file.read(8))
	return file.read(length)
