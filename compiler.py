# Crochet Pattern Markdown
# Compiler - compiler.py
# Georgia Klein
# CS111

import parser
from cromdDefinitions import pageNumberStyles, textColor, abbreviationDefinitions, hookSizes, textSizes
import sys
import os
from funcparserlib.parser import _Tuple

class Compiler():
    def __init__(self, inputFile, writeFile = None, textSize = None,
    textColor = None, headingColor = None):
        # Read the input file content into a string which can be parsed.
        pattern = open(inputFile)
        text = pattern.read()
        pattern.close()

        # Get the parser output.
        self.parsed = parser.loads(text)

        # writeFile is given when the file being compiled is being imported to
        # another file. 
        if writeFile:
            self.outputFile = writeFile
        else:
            self.outputFile = None

        # Global rules defaults.
        if textColor:
            self.textColor = textColor
        else:
            self.textColor = "black"

        if headingColor:
            self.headingColor = headingColor
        else:
            self.headingColor = "black"

        if textSize:
            self.textSize = textSize
        else:
            self.textSize = textSizes["medium"]

    def importLaTeX(self):
        # An imported file can only include imports and sections, no global rules.
        sections = Sections(self.parsed[0], self.outputFile, self.textSize,
        self.textColor, self.headingColor)
        sections.addToLaTeX()
    
    def produceLaTeX(self, outputName):
        # If we are producting LaTeX from scratch, we create the new output file.
        self.outputFile = open(outputName + ".tex", "w")      

        # Shape content out of the parser results.
        # The first value will always be a list of imports and/or sections.
        # The second section will always be the global rules in the tuple
        # ('global_rules', [list of rules]).
        sectionsParsed = self.parsed[0]
        globalRulesParsed = self.parsed[1][1]

        self.outputFile.write("\\documentclass{article}\n")

        # Add the required packages.
        for package in ["graphicx", "hyperref", "graphicx", "xcolor"]:
            self.outputFile.write("\\usepackage{" + package + "}\n")
        self.outputFile.write("\n")

        # Make it so there is no indent for each paragraph.
        self.outputFile.write("\setlength\parindent{0pt}\n\n")
        
        # Add the global rules.
        globalRules = GlobalRules(globalRulesParsed, self.outputFile)
        rules = globalRules.addToLaTeX()

        # Shape out the global rules.
        if 'text_color' in rules:
            self.textColor = rules['text_color']
        if 'heading_color' in rules:
            self.headingColor = rules['heading_color']
        if 'text_size' in rules:
            self.textSize = textSizes[rules['text_size']]

        # Add the pattern sections.
        sections = Sections(sectionsParsed, self.outputFile, self.textSize,
        self.textColor, self.headingColor)
        self.outputFile.write("\\begin{document}\n\n")
        sections.addToLaTeX()
        self.outputFile.write("\\end{document}\n")

        self.outputFile.close()

    def producePDF(self, outputName):
        # Run the command in the operating system to convert a LaTeX file to
        # a pdf.
        self.produceLaTeX(outputName) 
        os.system("pdflatex " + outputName + ".tex")

class Sections():
    def __init__(self, sections, outputFile, textSize, textColor, headingColor):
        self.sections = sections
        self.f = outputFile
        self.textSize = textSize
        self.textColor = textColor
        self.headingColor = headingColor

    def addToLaTeX(self):
        # The format will either be ('import', '"filename.cromd"') or
        # it will be a list of arguments where one argument is a type.
        for s in self.sections:
            if s[0] == 'import':
                self.addImport(s[1])
            else:
                self.addSection(s)

    def addImport(self, filename):
        self.f.write("% Content imported from " + filename + ".\n")

        # Create a new compiler object, passing in the LaTeX file that is
        # currently being written to and write to that file.
        importCompile = Compiler(filename, self.f, self.textSize, self.textColor, self.headingColor)
        importCompile.importLaTeX()

    def addSection(self, section):
        # A section will include the type and content.
        sectionDict = dict(section)
        content = sectionDict['content']

        # Based on the type of the pattern section, run different methods.
        match sectionDict['type']:
            case 'title_page':
                 self.addTitlePage(content)
            case 'project_details':
                 self.addProjectDetails(content)
            case 'pattern_section':
                 self.addPatternSection(content)
            case 'assembly':
                 self.addAssembly(content)
            case _:
                 raise Exception("Invalid page type: " + sType + ".")

    def writeSize(self, type):
        # Given the type of text, update the current text size.
        self.f.write("\\" + self.textSize[type] + "\n")

    def writeColor(self, color):
        # Update the text color.
        self.f.write("\color{" + color + "}\n")

    def addTitlePage(self, content):
        # Required arguments: title, author
        # Optional arguments: subtitle, image, hyperlink, space, text

        # Raise an error if a required section is missing.
        contentDict = dict(content)
        if not ('title' in contentDict):
            raise Exception("Missing argument 'title' from title page parameters.")
        if not ('author' in contentDict):
            raise Exception("Missing argument 'author' from title page parameters.")

        self.f.write("% Writing title page.\n")
        self.f.write("\\begin{titlepage}\n")
        self.f.write("\\begin{center}\n")
        self.writeColor(self.headingColor)

        # Information abut the LaTeX titlepage:
        # https://www.overleaf.com/learn/latex/How_to_Write_a_Thesis_in_LaTeX_(Part_5)%3A_Customising_Your_Title_Page_and_Abstract
        for (arg, value) in content:
            match arg:
                case 'title':
                    assert type(value) == str, f"title argument must be a string."
                    self.writeSize("title")
                    self.f.write("\\textbf{" + value + "}\n")
                    self.writeSize("text")
                    self.f.write("\n")

                case 'author':
                    assert type(value) == str, f"author argument must be a string."
                    self.writeSize("subtitle")
                    self.f.write("\\textbf{" + value + "}\n")
                    self.writeSize("text")
                    self.f.write("\n")

                case 'subtitle':
                    assert type(value) == str, f"subtitle argument must be a string."
                    self.f.write("\\textbf{" + value + "}\n\n")

                case 'image':
                    self.addImage(value)

                case 'hyperlink':
                    self.addHyperlink(value)

                case 'space':
                    assert (type(value) == int) or (type(value) == float), f"space argument must be an integer or float."
                    self.f.write("\\vspace*{" + str(value) + "cm}\n\n")

                case 'text':
                    assert type(value) == str, f"text argument must be a string"
                    self.f.write(value + "\\\\\n")

                case other:
                    raise Exception("Invalid argument '" + other + "' in title page parameters.")

        self.f.write("\\end{center}\n")
        self.f.write("\\end{titlepage}\n\n")
        self.writeColor(self.textColor)

    def addImage(self, content):
        # Required arguments: path, size

        # Raise an error if a required section is missing.
        contentDict = dict(content)
        if not ('path' in contentDict):
            raise Exception("Missing argument 'text' from image parameters.")
        if not ('size' in contentDict):
            raise Exception("Missing argument 'link' from image parameters.")

        assert type(contentDict['path']) == str, f"image path argument must be a string."
        assert (type(contentDict['size']) == float) or (type(contentDict['size']) == int), f"image size argument must be a number."
        
        self.f.write("\\includegraphics[width=" + str(contentDict['size']) + "\\textwidth]{" + contentDict['path'] + "}\n\n")

    def addHyperlink(self, content):
        # Required arguments: text, link

        # Raise an error if a required section is missing.
        contentDict = dict(content)
        if not ('text' in contentDict):
            raise Exception("Missing argument 'text' from hyperlink parameters.")
        if not ('link' in contentDict):
            raise Exception("Missing argument 'link' from hyperlink parameters.")

        assert type(contentDict['link']) == str, f"hyperlink link argument must be a string."
        assert type(contentDict['text']) == str, f"hyperlink text argument must be a string."
        
        self.f.write("\\href{" + contentDict['link'] + "}{" + contentDict['text'] + "}\\\\\n")

    def addProjectDetails(self, content):

        # Required arguments: materials, abbreviations
        # Optional arguments: notes, size, skill-level, default

        # Raise an error if a required section is missing.
        contentDict = dict(content)
        if not ('materials' in contentDict):
            raise Exception("Missing argument 'materials' from project details page parameters.")
        if not ('abbreviations' in contentDict):
            raise Exception("Missing argument 'abbreviations' from project details page parameters.")

        self.f.write("% Writing project details.\n")

        # The project details title is hard coded.
        self.writeSize("subtitle")
        self.writeColor(self.headingColor)
        self.f.write("\\textbf{Project Details}\n")
        self.writeSize("text")
        self.writeColor(self.textColor)
        self.f.write("\n")

        for (arg, value) in content:
            match arg:
                case 'materials':
                    self.addMaterials(value)

                case "abbreviations":
                    self.addAbbreviations(value)

                case 'notes':
                    assert type(value) == str, f"notes argument must be a string."
                    self.f.write("\\textbf{Notes}\\\\" + value + "\\\\\n\n")

                case 'size':
                    assert type(value) == str, f"size argument must be a string."
                    self.f.write("\\textbf{Size}\\\\" + value + "\\\\\n\n")

                case 'skill-level':
                    assert type(value) == str, f"skill-level argument must be a string."
                    self.f.write("\\textbf{Skill Level}\\\\" + value + "\\\\\n\n")

                case 'custom':
                    # In the case that it is custom, there is another set of
                    # rules including a heading and text value.
                    customDict = dict(value)

                    if not ('heading' in customDict):
                        raise Exception("Missing argument 'heading' from project details custom parameter.")
                    if not ('text' in customDict):
                        raise Exception("Missing argument 'text' from project details custom parameter.")

                    assert type(customDict['heading']) == str, f"custom heading argument must be a string."
                    assert type(customDict['text']) == str, f"custom text argument must be a string."

                    self.f.write("\\textbf{" + customDict['heading'] + "}\\\\" + customDict['text'] + "\\\\\n\n")

                case 'image':
                    self.addImage(value)

                case other:
                    raise Exception("Invalid argument '" + other + "' in project details page parameters.") 

    def addMaterials(self, content):
        # Required arguments: yarn, hook.
        # Optional arguments: other

        # Raise an error if a required section is missing.
        contentDict = dict(content)
        if not ('yarn' in contentDict):
            raise Exception("Missing argument 'yarn' from project details materials parameter.")
        if not ('hook' in contentDict):
            raise Exception("Missing argument 'text' from project details materials parameter.")

        self.f.write("\\textbf{Materials}\\\\\n")

        for (arg, value) in content:
            match arg:
                case 'yarn':
                    assert type(value) == str, f"materials yarn argument must be a string."
                    self.f.write("Yarn: " + value + "\\\\\n")

                case 'hook':
                    # Two options for hook, either the value is given or it is
                    # searched using the hook() function.
                    self.f.write("Hook Size: ")
                    if type(value) == str:
                        self.f.write(value + "\\\\\n")
                    elif type(value) == _Tuple:
                        letter = value[1][0]

                        # Lookup in the hookSizes dictionary as the hook function.
                        if not (letter in hookSizes):
                            raise Exception("Hook type " + letter + " is not a valid hook type.")
                        self.f.write(letter + " hook or " + hookSizes[letter] + "\\\\\n")
                    else:
                        raise Exception("materials hook argument must be a string or hook function.")

                case 'other':
                    assert type(value) == str, f"materials other argument must be a string."
                    self.f.write(value + "\\\\\n")

                case other:
                    raise Exception("Invalid argument '" + other + "' in project details materials parameter.")

        self.f.write("\n\n")

    def addPatternSection(self, content):

        # Required arguments: heading, list
        # Optional arguments: image

        # Raise an error if a required section is missing.
        contentDict = dict(content)
        if not ('heading' in contentDict):
            raise Exception("Missing argument 'heading' from pattern section parameters.")
        if not ('list' in contentDict):
            raise Exception("Missing argument 'list' from pattern section parameters.")

        self.f.write("% Writing a pattern section.\n")
        
        for (arg, value) in content:
            match arg:
                case 'heading':
                    assert type(value) == str, f"heading argument must be a string."
                    self.writeSize("subtitle")
                    self.writeColor(self.headingColor)
                    self.f.write("\\textbf{" + value + "}\n")
                    self.writeSize("text")
                    self.writeColor(self.textColor)
                    self.f.write("\n")

                case 'list':
                    self.addList(value)

                case 'image':
                    self.addImage(value)

                case 'space':
                    assert (type(value) == int) or (type(value) == float), f"space argument must be an integer or float."
                    self.f.write("\\vspace*{" + str(value) + "cm}\n\n")

                case 'text':
                    assert type(value) == str, f"text argument must be a string"
                    self.f.write(value + "\\\\\n")

                case other:
                    raise Exception("Invalid argument '" + other + "' in pattern section parameters.")

        self.f.write("\n\n")

    def addAssembly(self, content):
        # Required arguments: heading, list
        # Optional arguments: image

        # Raise an error if a required section is missing.
        contentDict = dict(content)
        if not ('heading' in contentDict):
            raise Exception("Missing argument 'heading' from assembly section parameters.")
        if not ('list' in contentDict):
            raise Exception("Missing argument 'list' from assembly section parameters.")

        self.f.write("% Writing an assembly section.\n")

        # Assembly title is hard coded.
        self.writeSize("subtitle")
        self.writeColor(self.headingColor)
        self.f.write("\\textbf{Assembly}\n")
        self.writeSize("text")
        self.writeColor(self.textColor)
        self.f.write("\n")

        for (arg, value) in content:
            match arg:
                case 'heading':
                    assert type(value) == str, f"heading argument must be a string."
                    self.f.write("\\textbf{" + value + "}\\\\\n")

                case 'list':
                    self.addList(value)

                case 'image':
                    self.addImage(value)

                case 'space':
                    assert (type(value) == int) or (type(value) == float), f"space argument must be an integer or float."
                    self.f.write("\\vspace*{" + str(value) + "cm}\n\n")

                case 'text':
                    assert type(value) == str, f"text argument must be a string"
                    self.f.write(value + "\\\\\n")

                case other:
                    raise Exception("Invalid argument '" + other + "' in assembly parameters.")

        self.f.write("\n\n")

    def addList(self, content):
        # A item in a list can either be just text, or, in order to have an
        # instruction repeat for multiple lines, the item can contain both the
        # number of times the instruction should be repeated and the instruction
        # as text.

        self.f.write("% Writing a list.\n")

        listLine = 1
        for (arg, value) in content:
            match arg:
                case 'text':
                    assert type(value) == str, f"text argument must be a string."
                    self.f.write(str(listLine) + ". " + value + "\\\\\n")
                    listLine += 1

                case 'items':
                    # In the case that there are items, there is another set of
                    # rules including a lines and text value.
                    itemsDict = dict(value)
                    
                    # Write repeated lines.
                    self.f.write(str(listLine) + "-" + str(listLine + itemsDict['lines']) + ". ")
                    self.f.write(itemsDict['text'] + "\\\\\n")

                    # Increment the line count by the number of repeats of the
                    # current line.
                    listLine += itemsDict['lines'] + 1

                case other:
                    raise Exception("Invalid argument '" + other + "' in list parameters.")

    def addAbbreviations(self, content):
        # Abbreviation can either be the function call populate_abbreviations()
        # or a dictionary of a term and definition.

        self.f.write("\\textbf{Abbreviations}\\\\\n")

        for (arg, value) in content:
            match arg:
                case 'custom':
                    # In the case that there is a custom abbreviation, there is
                    # another set of rules including a term and text value.
                    customDict = dict(value)

                    if not ('term' in customDict):
                        raise Exception("Missing argument 'term' from abbreviations parameters.")
                    if not ('text' in customDict):
                        raise Exception("Missing argument 'title' from abbreviation parameters.")

                    self.f.write(customDict['term'] + ": " + customDict['text'] + "\\\\\n")

                case 'load':
                    for term in value[1]:
                        self.f.write(term + ": " + abbreviationDefinitions[term] + "\\\\\n")

                case other:
                    raise Exception("Invalid argument '" + other + "' in abbrevations parameters.")

        self.f.write("\n\n")

class GlobalRules():
    def __init__(self, globalRules, outputFile):
        self.globalRules = globalRules
        self.f = outputFile

    def addToLaTeX(self):
        self.f.write("% Writing global rules.\n")

        rulesToReturn = {}

        # Based on the type of the global rule, run different methods.
        for rule in self.globalRules:
            match rule[0]:
                case 'page_numbers':
                    # Page number rules information:
                    # https://www.overleaf.com/learn/latex/Page_numbering
                    if rule[1] in pageNumberStyles:
                        self.f.write("\pagenumbering{" + rule[1] + "}\n\n")
                    else:
                        raise Exception("Invalid page number style, must be 'arabic', 'alph', 'Alph', 'roman' or 'Roman'.")

                # Coloring information:
                # https://www.overleaf.com/learn/latex/Using_colours_in_LaTeX
                # The user is allowed to set different colors for the page
                # background, the regular text color and the header text color.
                case 'page_color':
                    if rule[1] in textColor:
                        self.f.write("\pagecolor{" + rule[1] + "}\n\n")
                    else:
                        raise Exception("Invalid argument '" + rule[1] + "' for page color.")

                case 'text_color':
                    if rule[1] in textColor:
                        rulesToReturn['text_color'] = rule[1]
                    else:
                        raise Exception("Invalid argument '" + rule[1] + "' for text color.")

                case 'headers_color':
                    if rule[1] in textColor:
                        rulesToReturn['heading_color'] = rule[1]
                    else:
                        raise Exception("Invalid argument '" + rule[1] + "' for text color.")

                # There are three different schemas of text sizes defined in th
                # cromdDefinitions file, defined to be small, medium and large.
                case 'text_size':
                    if rule[1] in ["small", "medium", "large"]:
                        rulesToReturn['text_size'] = rule[1]
                    else:
                        raise Exception("Invalid argument '" + rule[1] + "' for text size.")

                case other:
                    raise Exception("Invalid argument '" + other + "' in global rules.")

        return rulesToReturn

def main():
    print("Compiling pattern in file: " + sys.argv[1])
    compiler = Compiler(sys.argv[1])

    # compiler.produceLaTeX("output")
    compiler.producePDF("output")

if __name__ == "__main__":
    main()
