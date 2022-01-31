#!/usr/bin/python3
from DskDb import *

from sys import argv as _argv
args=_argv[1:]
execdir=_argv[0]

from yaml import dump as _dump
from re import sub

def dump(stuff):
	return sub(r'\n(?!\s)', "\n\n", _dump(stuff))

def usage(*args): 
	print("Usage: readdb infile [outfile]")
	print("Reads a diskdb and dumps as yaml to [outfile] or stdout")
	if args: exit(args[0])
	else: exit(0)

if len(args)<1 or len(args)>2:
	usage()
elif args[0]=="-h":
	usage()

try:
	infile=open(args[0],"rb")
except FileNotFoundError:
	print(f"File `{args[0]}` not found!")
	usage(2)

try:
	if len(args)==2:
		outfile=open(args[1],"w")
		outfile.write(dump(diskDb.read(infile)))
	elif len(args)==1:
		print(dump(diskDb.read(infile)))
except diskDb.NoHeaderError:
	print(f"File `{args[0]}` is not a diskdb!")
	usage(1)