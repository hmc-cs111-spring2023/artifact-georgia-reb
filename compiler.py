import parser
import sys
import os
from funcparserlib.parser import _Tuple

class Compiler():
    def __init__(self, inputFile, writeFile = None):
        # Read the input file content into a string which can be parsed.
        pattern = open(inputFile)
        text = pattern.read()
        pattern.close()

        # Get the parser output.
        self.parsed = parser.loads(text)

        # whiteFile is given when the file being compiled is being imported to
        # another file. 
        if writeFile:
            self.outputFile = writeFile
            self.beingImported = True # TODO: do we want to use this?

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

        # These packages will be included in the LaTeX file.
        for package in ["graphicx", "hyperref", "graphicx"]:
            self.outputFile.write("\\usepackage{" + package + "}\n")
        self.outputFile.write("\n")

        # Make it so there is no indenet for a new paragraph.
        self.outputFile.write("\setlength\parindent{0pt}")
        
        # Add the global rules.
        globalRules.addToLaTeX(self.outputFile)

        # Add the pattern sections.
        self.outputFile.write("\\begin{document}\n\n")
        sections.addToLaTeX(self.outputFile)
        self.outputFile.write("\\end{document}\n")

        self.outputFile.close()

    def producePDF(self, outputName):
        # Run the command in the operating system to convert a LaTeX file to
        # a pdf.
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
        f.write("% Content imported from " + filename + ".\n")

        # Create a new compiler object, passing in the LaTeX file that is
        # currently being written to.
        importCompile = Compiler(filename, f)
        importCompile.importLaTeX()

    def addSection(self, f, section):
        sDict = dict(section)
        content = sDict['content']

        # Based on the type of the pattern section, run different methods.
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
        # Optional sections: subtitle, image, hyperlink, space, copyright
        if not ('title' in contentDict):
            raise Exception("Missing argument 'title' from title page parameters.")
        if not ('author' in contentDict):
            raise Exception("Missing argument 'author' from title page parameters.")

        f.write("% Writing title page.\n")
        f.write("\\begin{titlepage}\n")
        f.write("\\begin{center}\n")

        # TODO: add more formatting later!
        # https://www.overleaf.com/learn/latex/How_to_Write_a_Thesis_in_LaTeX_(Part_5)%3A_Customising_Your_Title_Page_and_Abstract
        # I should add the option to add text sizes, currently they are hard coded.
        for arg in contentDict:
            match arg:
                case 'title':
                    assert type(contentDict['title']) == str, f"title argument must be a string."
                    f.write("\\Huge\n")
                    f.write("\\textbf{" + contentDict['title'] + "}\n")
                    f.write("\\normalsize\n\n")

                case 'author':
                    assert type(contentDict['author']) == str, f"author argument must be a string."
                    f.write("\\LARGE\n")
                    f.write("\\textbf{" + contentDict['author'] + "}\n")
                    f.write("\\normalsize\n\n")

                case 'subtitle':
                    assert type(contentDict['subtitle']) == str, f"subtitle argument must be a string."
                    f.write("\\large\n")
                    f.write(contentDict['subtitle'] + "\n")
                    f.write("\\normalsize\n\n")

                case 'image':
                    assert type(contentDict['image']) == str, f"image argument must be a string."
                    f.write("\\includegraphics[width=\\textwidth]{" + contentDict['image'] + "}\n")

                case 'hyperlink':
                    self.addHyperlink(f, contentDict['hyperlink'])

                case 'space':
                    assert type(contentDict['space']) == int, f"space argument must be an integer or float."
                    f.write("\\vspace*{" + str(contentDict['space']) + "cm}")

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
        if not ('text' in contentDict):
            raise Exception("Missing argument 'text' from hyperlink parameters.")

        if not ('link' in contentDict):
            raise Exception("Missing argument 'link' from hyperlink parameters.")

        assert type(contentDict['link']) == str, f"hyperlink link argument must be a string."
        assert type(contentDict['text']) == str, f"hyperlink text argument must be a string."
        f.write("\\href{" + contentDict['link'] + "}{" + contentDict['text'] + "}\n")

    def addProjectDetails(self, f, content):
        contentDict = dict(content)

        # TODO: make this robust!!! there is a lot more to add
        # Required sections: materials, abbreviations
        # Optional sections: notes, size, skill-level, default

        if not ('materials' in contentDict):
            raise Exception("Missing argument 'materials' from project details page parameters.")
        if not ('abbreviations' in contentDict):
            raise Exception("Missing argument 'abbreviations' from project details page parameters.")

        f.write("% Writing project details.\n")

        # Currently the project details title is hard coded.
        f.write("\\huge\n")
        f.write("\\textbf{Project Details}\n")
        f.write("\\normalsize\n\n")

        for arg in contentDict:
            match arg:
                case 'materials':
                    self.addMaterials(f, contentDict['materials'])

                case "abbreviations":
                    self.addAbbreviations(f, contentDict['materials'])

                case 'notes':
                    assert type(contentDict['notes']) == str, f"notes argument must be a string."
                    f.write("\\textbf{Notes}\\\\" + contentDict['notes'] + "\\\\\n\n")

                case 'size':
                    assert type(contentDict['size']) == str, f"size argument must be a string."
                    f.write("\\textbf{Size}\\\\" + contentDict['size'] + "\\\\\n\n")

                case 'skill-level':
                    assert type(contentDict['skill-level']) == str, f"skill-level argument must be a string."
                    f.write("\\textbf{Skill Level}\\\\" + contentDict['skill-level'] + "\\\\\n\n")

                case 'custom':
                    customDict = dict(contentDict['custom'])

                    if not ('header' in customDict):
                        raise Exception("Missing argument 'header' from project details custom parameter.")
                    if not ('text' in customDict):
                        raise Exception("Missing argument 'text' from project details custom parameter.")

                    assert type(customDict['header']) == str, f"custom header argument must be a string."
                    assert type(customDict['text']) == str, f"custom text argument must be a string."

                    f.write("\\textbf{" + customDict['header'] + "}\\\\" + customDict['text'] + "\\\\\n\n")

                case other:
                    raise Exception("Invalid argument '" + other + "' in project details page parameters.") 

    def addMaterials(self, f, content):
        contentDict = dict(content)

        if not ('yarn' in contentDict):
            raise Exception("Missing argument 'yarn' from project details materials parameter.")
        if not ('hook' in contentDict):
            raise Exception("Missing argument 'text' from project details materials parameter.")

        f.write("\\textbf{Materials}\\\\\n")

        for arg in contentDict:
            match arg:
                case 'yarn':
                    assert type(contentDict['yarn']) == str, f"materials yarn argument must be a string."
                    f.write("Yarn: " + contentDict['yarn'] + "\\\\")

                case 'hook':
                    print(contentDict['hook'])
                    f.write("Hook: ")
                    if type(contentDict['hook']) == str:
                        f.write(contentDict['hook'] + "\\\\")
                    elif type(contentDict['hook']) == _Tuple:
                        if type(contentDict['hook'][1][0]) == str:
                            f.write(self.sizeToMM(contentDict['hook'][1][0]) + "\\\\")
                        else:
                            f.write(self.mmToSize(contentDict['hook'][1][0]) + "\\\\")
                    else:
                        raise Exception("materials hook argument must be a string or hook function.")

                case 'other':
                    assert type(contentDict['other']) == str, f"materials other argument must be a string."
                    f.write(contentDict['yarn'] + "\\\\")

                case other:
                    raise Exception("Invalid argument '" + other + "' in project details materials parameter.") 

        f.write("\n\n")

    def sizeToMM(self, size):
        # TODO write this conversion!
        return "Size " + size + ", 5mm."

    def mmToSize(self, mm):
        # TODO write this conversion!
        return "Size H, " + mm + "mm."

    def addAbbreviations(self, f, content):
        contentDict = dict(content)

        f.write("\\textbf{Abbreviations}\\\\\n\n")

class GlobalRules():
    def __init__(self, globalRules):
        self.globalRules = globalRules

    def addToLaTeX(self, f):
        f.write("% Writing global rules.\n")

        # Based on the type of the global rule, run different methods.
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
                    style = contentDict['style']

                    # https://www.overleaf.com/learn/latex/Page_numbering
                    if style in ["arabic", "alph", "Alph", "roman", "Roman"]:
                        f.write("\pagenumbering{" + style + "}\n\n")
                    else:
                        raise Exception("Invalid page number style, must be 'arabic', 'alph', 'Alph', 'roman' or 'Roman'.")

                case other:
                    raise Exception("Invalid argument '" + other + "' in page number global rule parameters.") 

def main():
    print("Compiling pattern in file: " + sys.argv[1])
    compiler = Compiler(sys.argv[1])

    compiler.producePDF("output")

if __name__ == "__main__":
    main()
