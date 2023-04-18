# Crochet Pattern Markdown
# Definitions - cromdDefinitions.py
# Georgia Klein
# CS111

# This file contains values that will be looked up by the compiler.

# Abbreviations source: https://www.craftyarncouncil.com/standards/crochet-abbreviations
abbreviationDefinitions = {"alt" : "alternate",
"approx" : "approximately",
"beg" : "begin/beginning",
"bet" : "between",
"BL" : "back loop",
"BLO" : "bback loop only",
"bo" : "bobble",
"BP" : "back post",
"BPdc" : "back post double crochet",
"BPdtr" : "back post double treble crochet",
"BPhdc" : "back post half double crochet",
"BPsc" : "back post single crochet",
"BPtr" : "back post treble crochet",
"CC" : "contrasting color",
"ch" : "chain stitch",
"ch-" : "refer to chain or space previously made, e.g., ch-1 space",
"ch-sp" : "chain space",
"CL" : "cluster",
"cont" : "continue",
"dc" : "double crochet",
"dc2tog" : "double crochet 2 stitches together",
"dec" : "decrease",
"dtr" : "double treble crochet",
"edc" : "extended double crochet",
"ehdc" : "extended half double crochet",
"esc" : "extended single crochet",
"etr" : "extended treble crochet",
"FL" : "front loop",
"FLO" : "front loop only",
"foll" : "following",
"FP" : "front post",
"FPdc" : "front post double crochet",
"FPdtr" : "front post double treble crochet",
"FPhdc" : "front post half double crochet",
"FPsc" : "front post single crochet",
"FPtr" : "front post treble crochet",
"hdc" : "half double crochet",
"hdc2tog" : "half double crochet 2 stitches together",
"inc" : "increase",
"lp" : "loop",
"m" : "marker",
"MC" : "main color",
"pat" : "pattern",
"patt" : "pattern",
"pc" : "popcorn stitch",
"pm" : "place marker",
"prev" : "previous",
"ps" : "puff stitch",
"puff" : "puff stitch",
"rem" : "remaining",
"rep" : "repeat",
"rnd" : "round",
"RS" : "right side",
"sc" : "single crochet",
"sc2tog" : "single crochet 2 stitches together",
"sh" : "shell",
"sk" : "skip",
"sl st" : "slip stitch",
"sm" : "slip marker",
"sl m" : "slip marker",
"sp" : "space",
"st" : "stitch",
"tbl" : "through back loop",
"tch" : "turning chain",
"t-ch" : "turning chain",
"tog" : "together",
"tr" : "treble crochet",
"tr2tog" : "treble crochet 2 stitches together",
"trtr" : "triple treble crochet",
"WS" : "wrong side",
"yo" : "yarn over",
"yoh" : "yarn over hook"}

# https://www.craftyarncouncil.com/standards/hooks-and-needles
hookSizes = {"B" : "2.25 mm",
"C" : "2.75 mm",
"D": "3.125-3.5 mm",
"E": "3.5 mm",
"F": "3.75 mm",
"G": "4-4.25 mm",
"H": "5 mm",
"I": "5.25-5.5 mm",
"J": "5.75-6 mm",
"K": "6.5 mm",
"L": "8 mm",
"M": "9 mm",
"N": "9-10 mm",
"P": "10-15 mm",
"Q": "15-16 mm",
"S": "19 mm",
"T": "25-30 mm",
"U": "25 mm",
"X": "25-30 mm"}

# https://www.overleaf.com/learn/latex/Using_colours_in_LaTeX
textColor = ["red", "green", "blue", "cyan", "magenta",
            "yellow", "black", "gray", "white", "darkgray", "lightgray",
            "brown", "lime", "olive", "orange", "pink", "purple",
            "teal", "violet"]

# https://www.overleaf.com/learn/latex/Page_numbering
pageNumberStyles = ["arabic", "alph", "Alph", "roman", "Roman"]

# Text size schema that I have created.
# title inclued the pattern title, subtitle includes the page titles and
# author, and text is the regular text size. 
# LaTeX font size info: https://latex-tutorial.com/changing-font-size/
smallText = {"title": "LARGE", "subtitle": "Large", "text" : "small"}
mediumText = {"title": "huge", "subtitle": "LARGE", "text" : "normalsize"}
largeText = {"title": "Huge", "subtitle": "huge", "text" : "Large"}
textSizes = {"small": smallText, "medium" : mediumText, "large": largeText}
