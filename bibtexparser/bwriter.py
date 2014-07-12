#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Francois Boulogne
# License:

import json
import logging

logger = logging.getLogger(__name__)

__all__ = ['to_bibtex', 'to_json']


def to_bibtex(parsed):
    """
    Convert parsed data to a bibtex string.
    All fields must be strings, which is the expected behavior without
    customization.

    :param parsed: BibTexParser object
    :returns: string -- bibtex
    :raises: TypeError if a field is not a string
    """
    data = parsed.get_entry_dict()
    bibtex = ''
    for entry in sorted(data.keys()):
        bibtex += '@' + data[entry]['type'] + '{' + data[entry]['id'] + ",\n"

        for field in [i for i in sorted(data[entry]) if i not in ['type', 'id']]:
            try:
                bibtex += " " + field + " = {" + data[entry][field] + "},\n"
            except TypeError:
                raise TypeError("The field %s in entry %s must be a string"
                                % (field, entry))
        bibtex += "}\n\n"
    return bibtex


def to_json(parsed):
    """
    Convert parsed data to json. This function is EXPERIMENTAL.

    :param parsed: BibTexParser object
    :returns: string -- json
    """
    return json.dumps(parsed.get_entry_dict(), sort_keys=True,
                      indent=4, separators=(',', ': '))
