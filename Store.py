from DskDb import *
from io import BytesIO

db=open("db.dskdb","w+b")

diskDb.store("hMM",db,force=True)
print(diskDb.read(db))