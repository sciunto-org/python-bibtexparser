#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from bibtexparser.customization import InvalidName, splitname

class TestSplitnameMethod(unittest.TestCase):
    def test_splitname_basic(self):
        """Basic tests of customization.splitname() """
        # Empty input.
        result = splitname("")
        expected = {}
        self.assertEqual(result, expected, msg="Invalid output for empty name")

        # Non-whitespace names.
        result = splitname("    ")
        expected = {}
        self.assertEqual(result, expected, msg="Invalid output for space-only name")
        result = splitname("  \t~~")
        expected = {}
        self.assertEqual(result, expected, msg="Invalid output for whitespace name")

        # Test strict mode.
        with self.assertRaises(InvalidName):         # Trailing comma (4 cases).
            splitname("BB,", strict_mode=True)
        with self.assertRaises(InvalidName):
            splitname("BB,  ", strict_mode=True)
        with self.assertRaises(InvalidName):
            splitname("BB, ~\t", strict_mode=True)
        with self.assertRaises(InvalidName):
            splitname(", ~\t", strict_mode=True)
        with self.assertRaises(InvalidName):         # Too many sections.
            splitname("AA, BB, CC, DD", strict_mode=True)
        with self.assertRaises(InvalidName):         # Unterminated opening brace (x3).
            splitname("AA {BB CC", strict_mode=True)
        with self.assertRaises(InvalidName):
            splitname("AA {{{BB CC", strict_mode=True)
        with self.assertRaises(InvalidName):
            splitname("AA {{{BB} CC}", strict_mode=True)
        with self.assertRaises(InvalidName):         # Unmatched closing brace (x3).
            splitname("AA BB CC}", strict_mode=True)
        with self.assertRaises(InvalidName):
            splitname("AA BB CC}}}", strict_mode=True)
        with self.assertRaises(InvalidName):
            splitname("{AA {BB CC}}}", strict_mode=True)

        # Test strict mode off for trailing comma.
        expected = {'first': [], 'von': [], 'last': ["BB"], 'jr': []}
        result = splitname("BB,", strict_mode=False)
        self.assertEqual(result, expected, msg="Invalid output for trailing comma with strict mode off")
        result = splitname("BB,   ", strict_mode=False)
        self.assertEqual(result, expected, msg="Invalid output for trailing comma with strict mode off")
        result = splitname("BB,  ~\t ", strict_mode=False)
        self.assertEqual(result, expected, msg="Invalid output for trailing comma with strict mode off")
        expected = {}
        result = splitname(",  ~\t", strict_mode=False)
        self.assertEqual(result, expected, msg="Invalid output for trailing comma with strict mode off")

        # Test strict mode off for too many sections.
        expected = {'first': ["CC", "DD"], 'von': [], 'last': ["AA"], 'jr': ["BB"]}
        result = splitname("AA, BB, CC, DD", strict_mode=False)
        self.assertEqual(result, expected, msg="Invalid output for too many sections with strict mode off")

        # Test strict mode off for an unterminated opening brace.
        result = splitname("AA {BB CC", strict_mode=False)
        expected = {'first': ["AA"], 'von': [], 'last': ["{BB CC}"], 'jr': []}
        self.assertEqual(result, expected, msg="Invalid output for unterminated opening brace with strict mode off")
        result = splitname("AA {{{BB CC", strict_mode=False)
        expected = {'first': ["AA"], 'von': [], 'last': ["{{{BB CC}}}"], 'jr': []}
        self.assertEqual(result, expected, msg="Invalid output for unterminated opening brace with strict mode off")
        result = splitname("AA {{{BB} CC}", strict_mode=False)
        expected = {'first': ["AA"], 'von': [], 'last': ["{{{BB} CC}}"], 'jr': []}
        self.assertEqual(result, expected, msg="Invalid output for unterminated opening brace with strict mode off")

        # Test strict mode off for an unmatched closing brace.
        result = splitname("AA BB CC}", strict_mode=False)
        expected = {'first': ["AA", "BB"], 'von': [], 'last': ["{CC}"], 'jr': []}
        self.assertEqual(result, expected, msg="Invalid output for unmatched closing brace with strict mode off")
        result = splitname("AA BB CC}}}", strict_mode=False)
        expected = {'first': ["AA", "BB"], 'von': [], 'last': ["{{{CC}}}"], 'jr': []}
        self.assertEqual(result, expected, msg="Invalid output for unmatched closing brace with strict mode off")
        result = splitname("{AA {BB CC}}}", strict_mode=False)
        expected = {'first': [], 'von': [], 'last': ["{{AA {BB CC}}}"], 'jr': []}
        self.assertEqual(result, expected, msg="Invalid output for unmatched closing brace with strict mode off")

        # Test it handles commas at higher brace levels.
        result = splitname("CC, dd, {AA, BB}")
        expected = {'first': ["{AA, BB}"], 'von': [], 'last': ["CC"], 'jr': ["dd"]}
        self.assertEqual(result, expected, msg="Invalid output for braced commas")


    def test_splitname_cases(self):
        """Test customization.splitname() vs output from BibTeX """
        for name, expected in splitname_test_cases:
            result = splitname(name)
            self.assertEqual(result, expected, msg="Input name: {0}".format(name))


splitname_test_cases = (
    (r'Per Brinch Hansen',
     {'first': ['Per', 'Brinch'], 'von': [], 'last': ['Hansen'], 'jr': []}),

    (r'Brinch Hansen, Per',
     {'first': ['Per'], 'von': [], 'last': ['Brinch', 'Hansen'], 'jr': []}),

    (r'Brinch Hansen,, Per',
     {'first': ['Per'], 'von': [], 'last': ['Brinch', 'Hansen'], 'jr': []}),

    (r"Charles Louis Xavier Joseph de la Vall{\'e}e Poussin",
     {'first': ['Charles', 'Louis', 'Xavier', 'Joseph'], 'von': ['de', 'la'],
      'last':  [r'Vall{\'e}e', 'Poussin'], 'jr': []}),

    (r'D[onald] E. Knuth',
     {'first': ['D[onald]', 'E.'], 'von': [], 'last': ['Knuth'], 'jr': []}),

    (r'A. {Delgado de Molina}',
     {'first': ['A.'], 'von': [], 'last': ['{Delgado de Molina}'], 'jr': []}),

    (r"M. Vign{\'e}",
     {'first': ['M.'], 'von': [], 'last': [r"Vign{\'e}"], 'jr': []}),

###############################################################################
#
# Test cases from
# http://maverick.inria.fr/~Xavier.Decoret/resources/xdkbibtex/bibtex_summary.html
#
###############################################################################

    (r'AA BB',
     {'first': ['AA'], 'von': [], 'last': ['BB'], 'jr': []}),

    (r'AA',
     {'first': [], 'von': [], 'last': ['AA'], 'jr': []}),

    (r'AA bb',
     {'first': ['AA'], 'von': [], 'last': ['bb'], 'jr': []}),

    (r'aa',
     {'first': [], 'von': [], 'last': ['aa'], 'jr': []}),

    (r'AA bb CC',
     {'first': ['AA'], 'von': ['bb'], 'last': ['CC'], 'jr': []}),

    (r'AA bb CC dd EE',
     {'first': ['AA'], 'von': ['bb', 'CC', 'dd'], 'last': ['EE'], 'jr': []}),

    (r'AA 1B cc dd',
     {'first': ['AA', '1B'], 'von': ['cc'], 'last': ['dd'], 'jr': []}),

    (r'AA 1b cc dd',
     {'first': ['AA'], 'von': ['1b', 'cc'], 'last': ['dd'], 'jr': []}),

    (r'AA {b}B cc dd',
     {'first': ['AA', '{b}B'], 'von': ['cc'], 'last': ['dd'], 'jr': []}),

    (r'AA {b}b cc dd',
     {'first': ['AA'], 'von': ['{b}b', 'cc'], 'last': ['dd'], 'jr': []}),

    (r'AA {B}b cc dd',
     {'first': ['AA'], 'von': ['{B}b', 'cc'], 'last': ['dd'], 'jr': []}),

    (r'AA {B}B cc dd',
     {'first': ['AA', '{B}B'], 'von': ['cc'], 'last': ['dd'], 'jr': []}),

    (r'AA \BB{b} cc dd',
     {'first': ['AA', r'\BB{b}'], 'von': ['cc'], 'last': ['dd'], 'jr': []}),

    (r'AA \bb{b} cc dd',
     {'first': ['AA'], 'von': [r'\bb{b}', 'cc'], 'last': ['dd'], 'jr': []}),

    (r'AA {bb} cc DD',
     {'first': ['AA', '{bb}'], 'von': ['cc'], 'last': ['DD'], 'jr': []}),

    (r'AA bb {cc} DD',
     {'first': ['AA'], 'von': ['bb'], 'last': ['{cc}', 'DD'], 'jr': []}),

    (r'AA {bb} CC',
     {'first': ['AA', '{bb}'], 'von': [], 'last': ['CC'], 'jr': []}),

    (r'bb CC, AA',
     {'first': ['AA'], 'von': ['bb'], 'last': ['CC'], 'jr': []}),

    (r'bb CC, aa',
     {'first': ['aa'], 'von': ['bb'], 'last': ['CC'], 'jr': []}),

    (r'bb CC dd EE, AA',
     {'first': ['AA'], 'von': ['bb', 'CC', 'dd'], 'last': ['EE'], 'jr': []}),

    (r'bb, AA',
     {'first': ['AA'], 'von': [], 'last': ['bb'], 'jr': []}),

    (r'bb CC,XX, AA',
     {'first': ['AA'], 'von': ['bb'], 'last': ['CC'], 'jr': ['XX']}),

    (r'bb CC,xx, AA',
     {'first': ['AA'], 'von': ['bb'], 'last': ['CC'], 'jr': ['xx']}),

    (r'BB,, AA',
     {'first': ['AA'], 'von': [], 'last': ['BB'], 'jr': []}),

    (r"Paul \'Emile Victor",
     {'first': ['Paul', r"\'Emile"], 'von': [], 'last': ['Victor'], 'jr': []}),

    (r"Paul {\'E}mile Victor",
     {'first': ['Paul', r"{\'E}mile"], 'von': [], 'last': ['Victor'], 'jr': []}),

    (r"Paul \'emile Victor",
     {'first': ['Paul'], 'von': [r"\'emile"], 'last': ['Victor'], 'jr': []}),

    (r"Paul {\'e}mile Victor",
     {'first': ['Paul'], 'von': [r"{\'e}mile"], 'last': ['Victor'], 'jr': []}),

    (r"Victor, Paul \'Emile",
     {'first': ['Paul', r"\'Emile"], 'von': [], 'last': ['Victor'], 'jr': []}),

    (r"Victor, Paul {\'E}mile",
     {'first': ['Paul', r"{\'E}mile"], 'von': [], 'last': ['Victor'], 'jr': []}),

    (r"Victor, Paul \'emile",
     {'first': ['Paul', r"\'emile"], 'von': [], 'last': ['Victor'], 'jr': []}),

    (r"Victor, Paul {\'e}mile",
     {'first': ['Paul', r"{\'e}mile"], 'von': [], 'last': ['Victor'], 'jr': []}),

    (r'Dominique Galouzeau de Villepin',
     {'first': ['Dominique', 'Galouzeau'], 'von': ['de'], 'last': ['Villepin'], 'jr': []}),

    (r'Dominique {G}alouzeau de Villepin',
     {'first': ['Dominique'], 'von': ['{G}alouzeau', 'de'],
      'last': ['Villepin'], 'jr': []}),

    (r'Galouzeau de Villepin, Dominique',
     {'first': ['Dominique'], 'von': ['Galouzeau', 'de'],
      'last': ['Villepin'], 'jr': []}),

###############################################################################
#
# Test cases from pybtex
# See file /pybtex/tests/parse_name_test.py in the pybtex source.
#
###############################################################################

    (r'A. E.                   Siegman',
     {'first': ['A.', 'E.'], 'von': [], 'last': ['Siegman'], 'jr': []}),

    (r'A. G. W. Cameron',
     {'first': ['A.', 'G.', 'W.'], 'von': [], 'last': ['Cameron'], 'jr': []}),

    (r'A. Hoenig',
     {'first': ['A.'], 'von': [], 'last': ['Hoenig'], 'jr': []}),

    (r'A. J. Van Haagen',
     {'first': ['A.', 'J.', 'Van'], 'von': [], 'last': ['Haagen'], 'jr': []}),

    (r'A. S. Berdnikov',
     {'first': ['A.', 'S.'], 'von': [], 'last': ['Berdnikov'], 'jr': []}),

    (r'A. Trevorrow',
     {'first': ['A.'], 'von': [], 'last': ['Trevorrow'], 'jr': []}),

    (r'Adam H. Lewenberg',
     {'first': ['Adam', 'H.'], 'von': [], 'last': ['Lewenberg'], 'jr': []}),

    (r'Addison-Wesley Publishing Company',
     {'first': ['Addison-Wesley', 'Publishing'], 'von': [],
      'last': ['Company'], 'jr': []}),

    (r'Advogato (Raph Levien)',
     {'first': ['Advogato', '(Raph'], 'von': [], 'last': ['Levien)'], 'jr': []}),

    (r'Andrea de Leeuw van Weenen',
     {'first': ['Andrea'], 'von': ['de', 'Leeuw', 'van'], 'last': ['Weenen'], 'jr': []}),

    (r'Andreas Geyer-Schulz',
     {'first': ['Andreas'], 'von': [], 'last': ['Geyer-Schulz'], 'jr': []}),

    (r'Andr{\'e} Heck',
     {'first': [r'Andr{\'e}'], 'von': [], 'last': ['Heck'], 'jr': []}),

    (r'Anne Br{\"u}ggemann-Klein',
     {'first': ['Anne'], 'von': [], 'last': [r'Br{\"u}ggemann-Klein'], 'jr': []}),

    (r'Anonymous',
     {'first': [], 'von': [], 'last': ['Anonymous'], 'jr': []}),

    (r'B. Beeton',
     {'first': ['B.'], 'von': [], 'last': ['Beeton'], 'jr': []}),

    (r'B. Hamilton Kelly',
     {'first': ['B.', 'Hamilton'], 'von': [], 'last': ['Kelly'], 'jr': []}),

    (r'B. V. Venkata Krishna Sastry',
     {'first': ['B.', 'V.', 'Venkata', 'Krishna'], 'von': [],
      'last': ['Sastry'], 'jr': []}),

    (r'Benedict L{\o}fstedt',
     {'first': ['Benedict'], 'von': [], 'last': [r'L{\o}fstedt'], 'jr': []}),

    (r'Bogus{\l}aw Jackowski',
     {'first': ['Bogus{\l}aw'], 'von': [], 'last': ['Jackowski'], 'jr': []}),

    (r'Christina A. L.\ Thiele',
     {'first': ['Christina', 'A.', 'L.\\'], 'von': [],
      'last': ['Thiele'], 'jr': []}),

    (r"D. Men'shikov",
     {'first': ['D.'], 'von': [], 'last': ["Men'shikov"], 'jr': []}),

    (r'Darko \v{Z}ubrini{\'c}',
     {'first': ['Darko'], 'von': [], 'last': [r'\v{Z}ubrini{\'c}'], 'jr': []}),

    (r'Dunja Mladeni{\'c}',
     {'first': ['Dunja'], 'von': [], 'last': [r'Mladeni{\'c}'], 'jr': []}),

    (r'Edwin V. {Bell, II}',
     {'first': ['Edwin', 'V.'], 'von': [], 'last': ['{Bell, II}'], 'jr': []}),

    (r'Frank G. {Bennett, Jr.}',
     {'first': ['Frank', 'G.'], 'von': [], 'last': ['{Bennett, Jr.}'], 'jr': []}),

    (r'Fr{\'e}d{\'e}ric Boulanger',
     {'first': [r'Fr{\'e}d{\'e}ric'], 'von': [], 'last': ['Boulanger'], 'jr': []}),

    (r'Ford, Jr., Henry',
     {'first': ['Henry'], 'von': [], 'last': ['Ford'], 'jr': ['Jr.']}),

    (r'mr Ford, Jr., Henry',
     {'first': ['Henry'], 'von': ['mr'], 'last': ['Ford'], 'jr': ['Jr.']}),

    (r'Fukui Rei',
     {'first': ['Fukui'], 'von': [], 'last': ['Rei'], 'jr': []}),

    (r'G. Gr{\"a}tzer',
     {'first': ['G.'], 'von': [], 'last': [r'Gr{\"a}tzer'], 'jr': []}),

    (r'George Gr{\"a}tzer',
     {'first': ['George'], 'von': [], 'last': [r'Gr{\"a}tzer'], 'jr': []}),

    (r'Georgia K. M. Tobin',
     {'first': ['Georgia', 'K.', 'M.'], 'von': [], 'last': ['Tobin'], 'jr': []}),

    (r'Gilbert van den Dobbelsteen',
     {'first': ['Gilbert'], 'von': ['van', 'den'], 'last': ['Dobbelsteen'], 'jr': []}),

    (r'Gy{\"o}ngyi Bujdos{\'o}',
     {'first': [r'Gy{\"o}ngyi'], 'von': [], 'last': [r'Bujdos{\'o}'], 'jr': []}),

    (r'Helmut J{\"u}rgensen',
     {'first': ['Helmut'], 'von': [], 'last': [r'J{\"u}rgensen'], 'jr': []}),

    (r'Herbert Vo{\ss}',
     {'first': ['Herbert'], 'von': [], 'last': ['Vo{\ss}'], 'jr': []}),

    (r"H{\'a}n Th{\^e}\llap{\raise 0.5ex\hbox{\'{\relax}}} Th{\'a}nh",
     {'first': [r'H{\'a}n', r"Th{\^e}\llap{\raise 0.5ex\hbox{\'{\relax}}}"],
      'von': [], 'last': [r"Th{\'a}nh"], 'jr': []}),

    (r"H{\`a}n Th\^e\llap{\raise0.5ex\hbox{\'{\relax}}} Th{\`a}nh",
     {'first': [r'H{\`a}n', r"Th\^e\llap{\raise0.5ex\hbox{\'{\relax}}}"],
      'von': [], 'last': [r"Th{\`a}nh"], 'jr': []}),

    (r'J. Vesel{\'y}',
     {'first': ['J.'], 'von': [], 'last': [r'Vesel{\'y}'], 'jr': []}),

    (r'Javier Rodr\'{\i}guez Laguna',
     {'first': ['Javier', r'Rodr\'{\i}guez'], 'von': [], 'last': ['Laguna'], 'jr': []}),

    (r'Ji\v{r}\'{\i} Vesel{\'y}',
     {'first': [r'Ji\v{r}\'{\i}'], 'von': [], 'last': [r'Vesel{\'y}'], 'jr': []}),

    (r'Ji\v{r}\'{\i} Zlatu{\v{s}}ka',
     {'first': [r'Ji\v{r}\'{\i}'], 'von': [], 'last': [r'Zlatu{\v{s}}ka'], 'jr': []}),

    (r'Ji\v{r}{\'\i} Vesel{\'y}',
     {'first': [r'Ji\v{r}{\'\i}'], 'von': [], 'last': [r'Vesel{\'y}'], 'jr': []}),

    (r'Ji\v{r}{\'{\i}}Zlatu{\v{s}}ka',
     {'first': [], 'von': [], 'last': [r'Ji\v{r}{\'{\i}}Zlatu{\v{s}}ka'], 'jr': []}),

    (r'Jim Hef{}feron',
     {'first': ['Jim'], 'von': [], 'last': ['Hef{}feron'], 'jr': []}),

    (r'J{\"o}rg Knappen',
     {'first': [r'J{\"o}rg'], 'von': [], 'last': ['Knappen'], 'jr': []}),

    (r'J{\"o}rgen L. Pind',
     {'first': [r'J{\"o}rgen', 'L.'], 'von': [], 'last': ['Pind'], 'jr': []}),

    (r'J{\'e}r\^ome Laurens',
     {'first': [r'J{\'e}r\^ome'], 'von': [], 'last': ['Laurens'], 'jr': []}),

    (r'J{{\"o}}rg Knappen',
     {'first': [r'J{{\"o}}rg'], 'von': [], 'last': ['Knappen'], 'jr': []}),

    (r'K. Anil Kumar',
     {'first': ['K.', 'Anil'], 'von': [], 'last': ['Kumar'], 'jr': []}),

    (r'Karel Hor{\'a}k',
     {'first': ['Karel'], 'von': [], 'last': [r'Hor{\'a}k'], 'jr': []}),

    (r'Karel P\'{\i}{\v{s}}ka',
     {'first': ['Karel'], 'von': [], 'last': [r'P\'{\i}{\v{s}}ka'], 'jr': []}),

    (r'Karel P{\'\i}{\v{s}}ka',
     {'first': ['Karel'], 'von': [], 'last': [r'P{\'\i}{\v{s}}ka'], 'jr': []}),

    (r'Karel Skoup\'{y}',
     {'first': ['Karel'], 'von': [], 'last': [r'Skoup\'{y}'], 'jr': []}),

    (r'Karel Skoup{\'y}',
     {'first': ['Karel'], 'von': [], 'last': [r'Skoup{\'y}'], 'jr': []}),

    (r'Kent McPherson',
     {'first': ['Kent'], 'von': [], 'last': ['McPherson'], 'jr': []}),

    (r'Klaus H{\"o}ppner',
     {'first': ['Klaus'], 'von': [], 'last': [r'H{\"o}ppner'], 'jr': []}),

    (r'Lars Hellstr{\"o}m',
     {'first': ['Lars'], 'von': [], 'last': [r'Hellstr{\"o}m'], 'jr': []}),

    (r'Laura Elizabeth Jackson',
     {'first': ['Laura', 'Elizabeth'], 'von': [], 'last': ['Jackson'], 'jr': []}),

    (r'M. D{\'{\i}}az',
     {'first': ['M.'], 'von': [], 'last': [r'D{\'{\i}}az'], 'jr': []}),

    (r'M/iche/al /O Searc/oid',
     {'first': [r'M/iche/al', r'/O'], 'von': [], 'last': [r'Searc/oid'], 'jr': []}),

    (r'Marek Ry{\'c}ko',
     {'first': ['Marek'], 'von': [], 'last': [r'Ry{\'c}ko'], 'jr': []}),

    (r'Marina Yu. Nikulina',
     {'first': ['Marina', 'Yu.'], 'von': [], 'last': ['Nikulina'], 'jr': []}),

    (r'Max D{\'{\i}}az',
     {'first': ['Max'], 'von': [], 'last': [r'D{\'{\i}}az'], 'jr': []}),

    (r'Merry Obrecht Sawdey',
     {'first': ['Merry', 'Obrecht'], 'von': [], 'last': ['Sawdey'], 'jr': []}),

    (r'Miroslava Mis{\'a}kov{\'a}',
     {'first': ['Miroslava'], 'von': [], 'last': [r'Mis{\'a}kov{\'a}'], 'jr': []}),

    (r'N. A. F. M. Poppelier',
     {'first': ['N.', 'A.', 'F.', 'M.'], 'von': [], 'last': ['Poppelier'], 'jr': []}),

    (r'Nico A. F. M. Poppelier',
     {'first': ['Nico', 'A.', 'F.', 'M.'], 'von': [], 'last': ['Poppelier'], 'jr': []}),

    (r'Onofrio de Bari',
     {'first': ['Onofrio'], 'von': ['de'], 'last': ['Bari'], 'jr': []}),

    (r'Pablo Rosell-Gonz{\'a}lez',
     {'first': ['Pablo'], 'von': [], 'last': [r'Rosell-Gonz{\'a}lez'], 'jr': []}),

    (r'Paco La                  Bruna',
     {'first': ['Paco', 'La'], 'von': [], 'last': ['Bruna'], 'jr': []}),

    (r'Paul                  Franchi-Zannettacci',
     {'first': ['Paul'], 'von': [], 'last': ['Franchi-Zannettacci'], 'jr': []}),

    (r'Pavel \v{S}eve\v{c}ek',
     {'first': ['Pavel'], 'von': [], 'last': [r'\v{S}eve\v{c}ek'], 'jr': []}),

    (r'Petr Ol{\v{s}}ak',
     {'first': ['Petr'], 'von': [], 'last': [r'Ol{\v{s}}ak'], 'jr': []}),

    (r'Petr Ol{\v{s}}{\'a}k',
     {'first': ['Petr'], 'von': [], 'last': [r'Ol{\v{s}}{\'a}k'], 'jr': []}),

    (r'Primo\v{z} Peterlin',
     {'first': [r'Primo\v{z}'], 'von': [], 'last': ['Peterlin'], 'jr': []}),

    (r'Prof. Alban Grimm',
     {'first': ['Prof.', 'Alban'], 'von': [], 'last': ['Grimm'], 'jr': []}),

    (r'P{\'e}ter Husz{\'a}r',
     {'first': [r'P{\'e}ter'], 'von': [], 'last': [r'Husz{\'a}r'], 'jr': []}),

    (r'P{\'e}ter Szab{\'o}',
     {'first': [r'P{\'e}ter'], 'von': [], 'last': [r'Szab{\'o}'], 'jr': []}),

    (r'Rafa{\l}\.Zbikowski',
     {'first': [], 'von': [], 'last': [r'Rafa{\l}\.Zbikowski'], 'jr': []}),

    (r'Rainer Sch{\"o}pf',
     {'first': ['Rainer'], 'von': [], 'last': [r'Sch{\"o}pf'], 'jr': []}),

    (r'T. L. (Frank) Pappas',
     {'first': ['T.', 'L.', '(Frank)'], 'von': [], 'last': ['Pappas'], 'jr': []}),

    (r'TUG 2004 conference',
     {'first': ['TUG', '2004'], 'von': [], 'last': ['conference'], 'jr': []}),

    (r'TUG {\sltt DVI} Driver Standards Committee',
     {'first': ['TUG', '{\sltt DVI}', 'Driver', 'Standards'], 'von': [],
      'last': ['Committee'], 'jr': []}),

    (r'TUG {\sltt xDVIx} Driver Standards Committee',
     {'first': ['TUG'], 'von': ['{\sltt xDVIx}'],
      'last': ['Driver', 'Standards', 'Committee'], 'jr': []}),

    (r'University of M{\"u}nster',
     {'first': ['University'], 'von': ['of'], 'last': [r'M{\"u}nster'], 'jr': []}),

    (r'Walter van der Laan',
     {'first': ['Walter'], 'von': ['van', 'der'], 'last': ['Laan'], 'jr': []}),

    (r'Wendy G.                  McKay',
     {'first': ['Wendy', 'G.'], 'von': [], 'last': ['McKay'], 'jr': []}),

    (r'Wendy McKay',
     {'first': ['Wendy'], 'von': [], 'last': ['McKay'], 'jr': []}),

    (r'W{\l}odek Bzyl',
     {'first': [r'W{\l}odek'], 'von': [], 'last': ['Bzyl'], 'jr': []}),

    (r'\LaTeX Project Team',
     {'first': [r'\LaTeX', 'Project'], 'von': [], 'last': ['Team'], 'jr': []}),

    (r'\rlap{Lutz Birkhahn}',
     {'first': [], 'von': [], 'last': [r'\rlap{Lutz Birkhahn}'], 'jr': []}),

    (r'{Jim Hef{}feron}',
     {'first': [], 'von': [], 'last': ['{Jim Hef{}feron}'], 'jr': []}),

    (r'{Kristoffer H\o{}gsbro Rose}',
     {'first': [], 'von': [], 'last': ['{Kristoffer H\o{}gsbro Rose}'], 'jr': []}),

    (r'{TUG} {Working} {Group} on a {\TeX} {Directory} {Structure}',
     {'first': ['{TUG}', '{Working}', '{Group}'], 'von': ['on', 'a'],
      'last': [r'{\TeX}', '{Directory}', '{Structure}'], 'jr': []}),

    (r'{The \TUB{} Team}',
     {'first': [], 'von': [], 'last': [r'{The \TUB{} Team}'], 'jr': []}),

    (r'{\LaTeX} project team',
     {'first': [r'{\LaTeX}'], 'von': ['project'], 'last': ['team'], 'jr': []}),

    (r'{\NTG{} \TeX{} future working group}',
     {'first': [], 'von': [], 'last': [r'{\NTG{} \TeX{} future working group}'], 'jr': []}),

    (r'{{\LaTeX\,3} Project Team}',
     {'first': [], 'von': [], 'last': [r'{{\LaTeX\,3} Project Team}'], 'jr': []}),

    (r'Johansen Kyle, Derik Mamania M.',
     {'first': ['Derik', 'Mamania', 'M.'], 'von': [], 'last': ['Johansen', 'Kyle'], 'jr': []}),

    (r"Johannes Adam Ferdinand Alois Josef Maria Marko d'Aviano Pius von und zu Liechtenstein",
     {'first': ['Johannes', 'Adam', 'Ferdinand', 'Alois', 'Josef', 'Maria', 'Marko'],
      'von': ["d'Aviano", 'Pius', 'von', 'und', 'zu'], 'last': ['Liechtenstein'], 'jr': []}),

    (r"Brand\~{a}o, F",
     {'first': ['F'], 'von': [], 'last': ['Brand\\', '{a}o'], 'jr': []}),
)


if __name__ == '__main__':
    unittest.main()
