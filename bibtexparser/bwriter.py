#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Francois Boulogne
# License:

def bibtex(parsed):
    """
    Convert parsed data to a bibtex string.

    :param parsed: BibTexParser object
    :returns: string -- bibtex
    """
    data = parsed.get_entry_dict()
    bibtex = ''
    for entry in sorted(data.keys()):
        bibtex += '@' + data[entry]['type'] + '{' + data[entry]['id'] + ",\n"

        for field in [i for i in sorted(data[entry]) if i not in ['type', 'id']]:
            bibtex += " " + field + " = {" + data[entry][field] + "},\n"
        bibtex += "}\n\n"
    return bibtex

