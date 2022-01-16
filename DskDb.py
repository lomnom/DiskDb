# supports ints, str, list and dict
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
		file.seek(0)
		header=file.read(len(self.header))
		if not force and header != self.header:
			raise NoHeaderWarning

		file.write(self.header)
		file.write(self.types[type(data)].encode(data)+b"\0\0")

	def read(self,file):
		header=file.read(len(self.header))
		if header != self.header:
			raise NoHeaderError

		header=file.read(2)
		return self.headers[header].decode(file)

class Storable:
	def __init__(self,stored,header):
		assert(type(header)==bytes)
		self.stored=stored
		self.header=header

	#returns header+data
	def encoder(self,func):
		self._encode=func

	def encode(self,file):
		return self._encode(self,file)

	#returns data+length
	def decoder(self,func):
		self._decode=func

	def decode(self,file):
		return self._decode(self,file)

diskDb=StoreSpec(b"DiskDb, another shitty database format!")

# Store integers
storeInt=Storable(int,b'\0i')
diskDb.addStorable(storeInt)

@storeInt.encoder
def encodeInt(spec,number):
	return spec.header+number.to_bytes(4,"big")

@storeInt.decoder
def decodeInt(spec,file):
	return int.from_bytes(file.read(4),"big")

# Strings
storeStr=Storable(str,b'\0s')
diskDb.addStorable(storeStr)

@storeStr.encoder
def encodeStr(spec,text):
	strData=bytes(text.encode("UTF8"))
	header=spec.header+len(strData).to_bytes(4,"big")
	return header+strData

@storeStr.decoder
def decodeStr(spec,file):
	length=int.from_bytes(file.read(4),"big")
	strData=str(file.read(length),encoding="UTF8")
	return strData

# Lists 
storeList=Storable(str,b'\0l')
diskDb.addStorable(storeList)
