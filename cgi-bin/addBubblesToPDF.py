#!/usr/sup/bin/python2.7
####!python2.7virt/venv/bin/python
import cgitb
cgitb.enable()
import sys,os

#sys.path.insert(0,'/h/cgregg/public_html/web/cgi-bin/python2.7virt/venv/lib/python2.7/site-packages/pyPdf')
# sys.stdout.write("Content-Type: text/html")
# sys.stdout.write("\n")
# sys.stdout.write("\n")

from pyPdf import PdfFileWriter, PdfFileReader

dataDir = "../data/"

def mergePDFs(inputName,outputName):
    outputFile = PdfFileWriter()
    inputFile = PdfFileReader(file(dataDir+inputName, "rb"))

    numPages = inputFile.getNumPages()
    watermark = PdfFileReader(file(dataDir+"bubbleOverlay.pdf", "rb"))

    for i in range(numPages):
        page = inputFile.getPage(i)
        if i==0:
            page.mergePage(watermark.getPage(0))
        outputFile.addPage(page)

    ## finally, write "output" to document-output.pdf
    outputStream = file(dataDir+outputName, "wb")
    outputFile.write(outputStream)
    outputStream.close()

if __name__ == "__main__":
    inputName = sys.argv[1]
    outputName = sys.argv[2]
    mergePDFs(inputName,outputName)