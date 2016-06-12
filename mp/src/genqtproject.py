#!/usr/bin/env python

from sys import argv
import os
from os.path import basename

def isAlphabet(ch):
	return (ord(ch) >= ord('A') and \
	ord(ch) <= ord('Z')) or \
	(ord(ch) >= ord('a') and \
	ord(ch) <= ord('z'))

def isNumber(ch):
	return ord(ch) >= ord('0') and \
	ord(ch) <= ord('9')

def getValue(line, key):
	# For ease of detection.
	line = line.replace("\\", "/") + "\n"

	length = len(line)
	WHITESPACE = [" ", "\t", "\n"]
	ALLOWED_CHARS = ["/", ".", ",", "_", "-"]

	idx = line.find(key)

	if idx < 0:
		return False, ""
	
	# Wind on
	idx = idx + len(key)
	
	# Wind on through whitespace
	while (idx < length and line[idx] in WHITESPACE):
		idx = idx + 1
	
	if idx >= length:
		return False, ""

	# We've found a non-whitespace character!
	idx2 = idx

	if line[idx] == '"':
		# Search for the next quote
		idx = idx + 1
		idx2 = idx + 1

		while (idx2 < length):
			if line[idx2] == '"':
				break
			idx2 = idx2 + 1

		if idx2 >= length:
			return False, ""

		return True, line[idx:idx2]

	else:
		# Search for the next invalid character
		idx2 = idx + 1

		while (idx2 < length):
			if not isAlphabet(line[idx2]) and not isNumber(line[idx2]) and \
			line[idx2] not in ALLOWED_CHARS:
				break
			idx2 = idx2 + 1

		if idx2 >= length:
			return False, ""

		return True, line[idx:idx2]

def getSourceFileName(line):
	success, filename = getValue(line, "$File")
	if success:
		return filename
	else:
		return ""

def handleFilePrefix(path, relativewd):
	# If the string begins with $SRCDIR/, replace this with nothing.
	# We take SRCDIR to be our current directory.
	srclen = len("$SRCDIR/")
	if len(path) > srclen and \
	path[0:srclen] == "$SRCDIR/":
		return path[srclen:]

	# Otherwise, add a prefix for the file wd relative to our wd.
	else:
		return relativewd + "/" + path

def extractFileNames(contents, relativewd):
	out = []

	for line in contents:
		fname = getSourceFileName(line)
		if fname != "":
			fname = handleFilePrefix(fname, relativewd)
			out.append(fname)
	
	return out

def splitSourceAndHeaderFiles(files):
	headers = []
	src = []

	for f in files:
		# Quick and dirty
		if f[len(f)-1] == "h":
			headers.append(f)
		else:
			src.append(f)

	return headers, src

def generateProFile(name, headers, sources):
	preamble = "TARGET = " + name + "\nTEMPLATE = app\n"
	headerString = "HEADERS +="
	sourcesString = "SOURCES +="

	for h in headers:
		headerString = headerString + " \\\n\t" + h
	
	for s in sources:
		sourcesString = sourcesString + " \\\n\t" + s

	out = preamble + "\n"
	if len(headers) > 0:
		out = out + headerString + "\n"
	if len(sources) > 0:
		out = out + sourcesString + "\n"

	return out

def getIncludedFiles(contents, relativewd):
	includes = []

	for line in contents:
		success, filename = getValue(line, "$Include")
		if success:
			filename = handleFilePrefix(filename, relativewd)
			includes.append(filename)
	
	return includes

def getFilesFromVPC(filename):
	contents = []
	f = None

	print("==============================")

	wd = os.getcwd()
	print("Working directory: " + wd)
	filewd = os.path.dirname(os.path.realpath(filename))
	print("File directory: " + filewd)

	relativewd = filewd.replace(wd + "/", "")
	print("Relative to working directory: " + relativewd)

	fileBasename = os.path.splitext(basename(filename))[0]
	print("File name: " + fileBasename)

	try:
		f = open(filename, "r")
		contents = f.readlines()
	
	except IOError:
		print("Unable to open file: check it exists and is not already open.")

	finally:
		if f is not None:
			f.close()

	print("File has " + str(len(contents)) + " lines")
	includes = getIncludedFiles(contents, relativewd)
	print(str(len(includes)) + " included files detected")
	contents = extractFileNames(contents, relativewd)
	headerFiles, sourceFiles = splitSourceAndHeaderFiles(contents)
	print(str(len(contents)) + " files detected: " + str(len(headerFiles)) \
	+ " header files and " + str(len(sourceFiles)) + " source files")

	print("==============================")

	return fileBasename, includes, headerFiles, sourceFiles

scriptname, inputfile = argv

files = [ inputfile ]
previous = []

baseName = ""
headerFiles = []
sourceFiles = []

while (len(files) > 0):
	print("Files remaining: " + str(len(files)))
	print("Processing: " + files[0])
	base, includes, headers, sources = getFilesFromVPC(files[0])
	
	if baseName == "":
		baseName = base
	
	headerFiles = headerFiles + headers
	sourceFiles = sourceFiles + sources

	print("\nNumber of includes to queue: " + str(len(includes)))
	for inc in includes:
		if inc not in previous:
			print(inc)
			files.append(inc)
		else:
			print(inc + " (already processed)")
	
	previous.append(files[0])
	files.pop(0)
	print("")

print(str(len(headerFiles)) + " headers and " \
+ str(len(sourceFiles)) + " source files discovered in total.")

if ( baseName == "" ):
	print("Unable to parse original file, exiting.")
	sys.exit()

outputPro = os.getcwd() + "/" + baseName + ".pro"
proContents = generateProFile(baseName, headerFiles, sourceFiles)

pro = None
try:
	pro = open(outputPro, "w")
	pro.write(proContents)

except IOError:
	print("Unable to write .pro file " + outputPro)

finally:
	if pro is not None:
		pro.close()

print("Output written to: " + outputPro)
