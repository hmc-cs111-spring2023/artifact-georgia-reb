# Crochet Pattern Markdown
# Parser - parser.py
# Georgia Klein
# CS111

from typing import List, Union
from funcparserlib.lexer import make_tokenizer, TokenSpec, Token, LexerError
from funcparserlib.parser import NoParseError, Parser, tok, many, forward_decl, finished, maybe
import sys

# Code is inspired by https://github.com/vlasovskikh/funcparserlib/blob/master/tests/json.py

# # # # # # # # # # #
# Tokenizer
# # # # # # # # # # #

# Given a list of strings, create a regular expression that accepts only those strings.
def regex_list(words):
    regex_words = r""
    for word in words:
        regex_words += "(" + word + ")|"

    regex_words = regex_words[:-1]
    return regex_words

# Keywords for our language.
page_types = ["title_page", "project_details", "pattern_section", "assembly"]
global_rules = ["global_rules", "page_numbers", "text_color", "headers_color",
"page_color", "text_size"]
section = ["import", "type", "content"]

section_content = ["title", "subtitle", "author", "hyperlink", "link",
"copyright", "size", "image", "text", "space", "materials", "yarn",
"hook", "other", "abbreviations", "notes", "size", "skill-level", "custom",
"heading", "list", "items", "lines", "term", "load", "path"]
functions = ["magic_ring", "populate_abbreviations"]

keywords = page_types + global_rules + section + section_content + functions

def tokenize(s: str) -> List[Token]:
    specs = [
        TokenSpec("whitespace", r"\s+"),
        TokenSpec("float", r"[+\-]?\d+\.\d*([Ee][+\-]?\d+)*"),
        TokenSpec("int", r"[+\-]?\d+"),
        TokenSpec("file", r"([^\"]*)\.cromd"),
        TokenSpec("op", r"[():{},\"]"),
        TokenSpec("keyword", regex_list(keywords)),
        TokenSpec("comment", r"#(.*)\n"),
        TokenSpec("string", r"[^\"]*"),
    ]
    tokenizer = make_tokenizer(specs)
    # Remove any whitespace and comments.
    return [t for t in tokenizer(s) if not (t.type in ["whitespace", "comment"])]

# # # # # # # # # # #
# Parser Combinator
# # # # # # # # # # #

def parse(tokens):
    int_num = tok("int") >> int
    float_num = tok("float") >> float
    keyword = tok("keyword").named("key")

    # Return a parser that parses a Token and returns the string value of the token
    # if the token is equivalent to the argument name.
    def op(name: str) -> Parser[Token, str]:
        return tok("op", name)

    string = -op("\"") + (tok("string") | (int_num | float_num) + tok("string")) + -op("\"")

    # An argument can be a number (int or float), a string, a keyword or a function call.
    function_call = forward_decl().named("function call")
    number = (int_num | float_num).named("number")
    argument = (string | number | keyword | function_call).named("argument")

    # A function call is a keyword followed by () with 0+ arguments in the parentheses.
    function_call.define(keyword + -op("(") + many(argument + -op(",")) + -op(")"))

    # A section can be many key-value pairs, where a value can be another section
    # or an argument.
    section = forward_decl().named("pattern section")
    value = (section | function_call | argument).named("value")
    section.define(-op("{") + many(keyword + -op(":") + value + -op(",")) + -op("}"))

    # A global rule is a keyword followed by 
    global_rules = (tok("keyword", "global_rules") + -op(":") + section).named("global rule")

    # You can import a section from a different file or write the section directly in the file.
    filename = (-op("\"") + tok("file") + -op("\"")).named("filename")
    import_section = (tok("keyword", "import") + -op(":") + filename).named("import pattern section")

    # Finished throws an error if there are any unparsed tokens left in the sequence.
    pattern = (many(section | import_section) + maybe(global_rules) + -finished).named("crochet pattern")

    return pattern.parse(tokens)

def loads(s):
    return parse(tokenize(s))

def main():
    print("Parsing pattern in file: " + sys.argv[1])
    pattern = open(sys.argv[1])
    text = pattern.read()
    print(loads(text))
    pattern.close()

if __name__ == "__main__":
    main()
