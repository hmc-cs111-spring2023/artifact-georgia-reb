import parser
import sys
import os

class Compiler():
    def __init__(self, inputFile, writeFile = None):
        # Read the input file content into self.text.
        pattern = open(inputFile)
        self.text = pattern.read()
        pattern.close()

        # Get the parser output.
        self.parsed = parser.loads(self.text)

        # Manage file to write to.
        if writeFile:
            self.outputFile = writeFile
            self.heading = False

    def importLaTeX(self):
        # An imported file can only include imports and sections, no global rules.
        sections = Sections(self.parsed[0])
        sections.addToLaTeX(self.outputFile)
    
    def produceLaTeX(self, outputName):
        self.outputFile = open(outputName + ".tex", "w")      

        # Shape content out of the parser results.
        # The first value will always be a list of imports and/or sections.
        # The second section will always be the global rules in the tuple
        # ('global_rules', [list of rules]).
        sections = Sections(self.parsed[0])
        globalRules = GlobalRules(self.parsed[1][1])

        self.outputFile.write("\\documentclass{article}\n")
        # TODO: clean up this formatting to be a loop?
        self.outputFile.write("\\usepackage{graphicx}\n\\usepackage{hyperref}\n\\usepackage{graphicx}\n\n")

        globalRules.addToLaTeX(self.outputFile)

        self.outputFile.write("\\begin{document}\n\n")
        sections.addToLaTeX(self.outputFile)
        self.outputFile.write("\\end{document}\n")

        self.outputFile.close()

    def producePDF(self, outputName):
        self.produceLaTeX(outputName) 
        os.system("pdflatex " + outputName + ".tex")

class Sections():
    def __init__(self, sections):
        self.sections = sections

    def addToLaTeX(self, f):

        # The format will either be ('import', '"filename.cromd"') or
        # it will be a list of arguments where one argument is a type.
        for s in self.sections:
            if s[0] == 'import':
                self.addImport(f, s[1])
            else:
                self.addSection(f, s)

    def addImport(self, f, filename):
        f.write("% Importing content from " + filename + ".\n")

        importCompile = Compiler(filename[1:-1], f)
        importCompile.importLaTeX()

    def addSection(self, f, section):
        sDict = dict(section)
        content = sDict['content']

        match sDict['type']:
            case 'title_page':
                 self.addTitlePage(f, content)
            case 'project_details':
                 self.addProjectDetails(f, content)
            case _:
                 msg = "Invalid page type: " + sType + "."
                 raise Exception(msg)

    def addTitlePage(self, f, content):
        contentDict = dict(content)

        # Required sections: title, author
        # Optional sections: subtitle, image, hyperlink, copyright
        if not ('title' in contentDict):
            raise Exception("Missing argument 'title' from title page parameters.")
        if not ('author' in contentDict):
            raise Exception("Missing argument 'author' from title page parameters.")

        f.write("% Writing title page.\n")
        f.write("\\begin{titlepage}\n")
        f.write("\\begin{center}\n")

        # TODO: add more formatting later!
        # https://www.overleaf.com/learn/latex/How_to_Write_a_Thesis_in_LaTeX_(Part_5)%3A_Customising_Your_Title_Page_and_Abstract
        # I should add the option to add text sizes.
        for arg in contentDict:
            match arg:
                case 'title':
                    # TODO: allow the user to specify the text size.
                    f.write("\\textbf{" + contentDict['title'][1:-1] + "}\n\n")

                case 'author':
                    f.write("\\textbf{" + contentDict['author'][1:-1] + "}\n\n")

                case 'subtitle':
                    f.write(contentDict['subtitle'][1:-1] + "\n\n")

                case 'image':
                    f.write("\\includegraphics[width=\\textwidth]{" + contentDict['image'][1:-1] + "}\n")

                case 'hyperlink':
                    self.addHyperlink(f, contentDict['hyperlink'])

                case 'copyright':
                    # TODO: fully complete this later
                    f.write("copyright\n\n")

                case other:
                    raise Exception("Invalid argument '" + other + "' in title page parameters.")

        f.write("\\end{center}\n")
        f.write("\\end{titlepage}\n\n")

    def addHyperlink(self, f, content):
        contentDict = dict(content)

        # Required sections: text, link
        # TODO: WHAT DO I DO HERE ABOUT OPTIONAL VALUES
        if not ('text' in contentDict):
            raise Exception("Missing argument 'text' from hyperlink parameters.")

        if not ('link' in contentDict):
            raise Exception("Missing argument 'link' from hyperlink parameters.")

        f.write("\\href{" + contentDict['link'][1:-1] + "}{" + contentDict['text'][1:-1] + "}\n")

    def addProjectDetails(self, f, content):
        contentDict = dict(content)

        # TODO: make this robust!!! there is a lot more to add
        # Required sections: title
        # Optional sections: text, image, hyperlink
        if not ('title' in contentDict):
            raise Exception("Missing argument 'title' from project details page parameters.")

        f.write("% Writing project details.\n")

        for arg in contentDict:
            match arg:
                case 'title':
                    f.write("\\textbf{" + contentDict['title'][1:-1] + "}\n\n")

                case 'text':
                    f.write(contentDict['text'][1:-1] + "\n\n")

                case 'image':
                    f.write("\\includegraphics[width=\\textwidth]{" + contentDict['image'][1:-1] + "}\n")

                case 'hyperlink':
                    self.addHyperlink(f, contentDict['hyperlink'])

                case other:
                    raise Exception("Invalid argument '" + other + "' in project details page parameters.") 

class GlobalRules():
    def __init__(self, globalRules):
        self.globalRules = globalRules

    def addToLaTeX(self, f):
        f.write("% Writing global rules.\n")

        for rule in self.globalRules:
            if rule[0] == 'page_numbers':
                self.addPageNumbers(f, rule[1])

    def addPageNumbers(self, f, content):
        contentDict = dict(content)

        # TODO: make this robust!!! there is a lot more to add
        # Required sections: style
        # Optional sections: text
        if not ('style' in contentDict):
            raise Exception("Missing argument 'syle' from page number global rule parameters.")

        for arg in contentDict:
            match arg:
                case 'style':
                    style = contentDict['style'][1:-1]

                    # https://www.overleaf.com/learn/latex/Page_numbering
                    if style in ["arabic", "alph", "Alph", "roman", "Roman"]:
                        f.write("\pagenumbering{" + style + "}\n\n")
                    else:
                        raise Exception("Invalid page number style.")

                case other:
                    raise Exception("Invalid argument '" + other + "' in page number global rule parameters.") 

# We can have functions that do the same as this:
# https://github.com/hmc-cs-131-spring-2023/cs-131-hw-5-gklein-hw5/blob/main/PostScript.hs
# Essentially you just pass in the arguments and then write to the output file.

# The more that I think about this, the more that I think I should write a
# class. Does that make sense?
# def makeTitlePage(name, author):

# thoughts:
# each class can produce a LaTeX section (knowing it will be imbeded in a larger file)
# each kind of thing corresponds to producting a piece of LaTeX
# the parser itself could be responsible for instantiating an object of the
# appropriate class
# OR
# the parser could just do my parse tree, then go through and continue
# currently I have a syntax data structure


# maybe then have an overall class that does something like toLatex which would
# print for the entire text


def main():
    print("Compiling pattern in file: " + sys.argv[1])
    compiler = Compiler(sys.argv[1])

    compiler.producePDF("output")

if __name__ == "__main__":
    main()
