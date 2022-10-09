import bibtexparser
name = "{G{\'{e}}rard} {Ben Arous}"
print(name)
print( bibtexparser.customization.getnames([name]))
print( bibtexparser.customization.getnames(["{Jean César}"]))
