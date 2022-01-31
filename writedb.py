#!/usr/bin/python3
from DskDb import *

from sys import argv as _argv
args=_argv[1:]
execdir=_argv[0]

from yaml import safe_load, dump
import yaml
from os.path import exists

def usage(*args): 
	print("Usage: writedb [-f] outfile infile")
	print("Reads yaml from [infile] or stdin, and writes to outfile")
	print("Add -f to overwrite an existing non-diskdb file")
	if args: exit(args[0])
	else: exit(0)

if not (len(args)==2 or len(args)==3):
	usage()

if len(args)==3:
	if args[0]=="-f":
		print("Overwriting file!")
		force=True
		args=args[1:]
	else:
		usage(1)
else:
	force=False

if (not force) and exists(args[0]) :
	outfile=open(args[0],'rb')
	try:
		diskDb.read(outfile)
	except diskDb.NoHeaderError:
		print(f"File `{args[0]}` is not a diskdb! Use -f to overwrite file!")
		usage(2)

outfile=open(args[0],"wb")
try:
	infile=open(args[1],"r")
except FileNotFoundError:
	print(f"File {args[1]} not found!")
	usage(2)

try:
	diskDb.store(safe_load(infile.read()),outfile)
except yaml.scanner.ScannerError:
	print(f"File `{args[1]}` contains invalid yaml!")
	usage(1)