from typing import Dict

import pytest as pytest

from bibtexparser.library import Library
from bibtexparser.model import ImplicitComment, ExplicitComment
from bibtexparser.splitter import Splitter

example_bibstr = """

@string{goossens = "Goossens, Michel"}

This line is an implicit comment.

@article{FuMetalhalideperovskite2019,
    author = "Yongping Fu and Haiming Zhu and Jie Chen and Matthew P. Hautzinger and X.-Y. Zhu and Song Jin",
    doi = {10.1038/s41578-019-0080-9},
    journal = {Nature Reviews Materials},
    month = {feb},
    number = {3},
    pages = {169-188},
    publisher = {Springer Science and Business Media {LLC}},
    title = {Metal halide perovskite nanostructures for optoelectronic applications and the study of physical properties},
    url = {https://www.nature.com/articles/s41578-019-0080-9},
    volume = {4},
    year = 2019
}

@comment{
    This is a comment.
    Spanning over two lines.
}

@preamble{e = mc^2}

@article{SunEnablingSiliconSolar2014,
    author = {Ke Sun and Shaohua Shen and Yongqi Liang and Paul E. Burrows and Samuel S. Mao and Deli Wang},
    doi = {10.1021/cr300459q},
    journal = {Chemical Reviews},
    month = {aug},
    number = {17},
    pages = {8662-8719},
    publisher = {American Chemical Society ({ACS})},
    title = "This title is missing a closing quote,
    url = {http://pubs.acs.org/doi/10.1021/cr300459q},
    volume = {114},
    year = {2014}
}


@string{mittelbach="Mittelbach, Franck"}

@article{LiuPhotocatalytichydrogenproduction2016,
    author = {Maochang Liu and Yubin Chen and Jinzhan Su and Jinwen Shi and Xixi Wang and Liejin Guo},
    doi = {10.1038/nenergy.2016.151},
    impactfactor = {54.000},
    journal = {Nature Energy},
    month = {sep},
    number = {11},
    pages = {16151},
    publisher = {Springer Science and Business Media {LLC}},
    title = {Photocatalytic hydrogen production using twinned nanocrystals and an unanchored {NiSx} co-catalyst},
    url = {http://www.nature.com/articles/nenergy2016151},
    volume = {1},
    year = {2016}
}


@Comment{This is another comment}

"""


def _split() -> Library:
    return Splitter(example_bibstr).split()


@pytest.mark.parametrize("expected", [
    {'position': 0, 'str_position': 0, 'key': 'goossens', 'value': "\"Goossens, Michel\"",
     'raw': '@string{goossens = "Goossens, Michel"}', "line": 2},
    {'position': 6, 'str_position': 1, 'key': 'mittelbach', 'value': "\"Mittelbach, Franck\"",
     'raw': '@string{mittelbach="Mittelbach, Franck"}', "line": 42},
])
def test_strings(expected: Dict[str, any]) -> None:
    library = _split()
    assert len(library.strings) == 2
    # Raise KeyError if not found
    tested_string = library.strings_dict[expected['key']]
    # Test parsed conent
    assert tested_string is not None
    assert tested_string.value == expected['value']
    assert tested_string.key == expected['key']
    assert tested_string.raw == expected['raw']
    assert tested_string.start_line == expected['line']
    # Make sure list and dict entries are the same, and position in list matches
    assert library.strings[expected['str_position']] == tested_string
    # Make sure position in overall blocks matches
    assert library.blocks[expected['position']] == tested_string


def test_preamble():
    library = _split()
    assert len(library.preambles) == 1
    preamble = library.preambles[0]
    assert preamble.raw == '@preamble{e = mc^2}'
    assert preamble.value == 'e = mc^2'
    assert preamble.start_line == 25


@pytest.mark.parametrize("expected", [
    # The first (implicit comment)
    {
        'position': 1, 'comment_position': 0, 'type': 'ImplicitComment',
        'raw': 'This line is an implicit comment.',
        'line': 4, 'comment': 'This line is an implicit comment.'
    },
    # The second (explicit comment)
    {
        'position': 3, 'comment_position': 1, 'type': 'ExplicitComment',
        'raw': '@comment{\n    This is a comment.\n    Spanning over two lines.\n}',
        'line': 20, 'comment': 'This is a comment.\n    Spanning over two lines.'
    },
    # The third (explicit comment)
    {
        'position': 8, 'comment_position': 2, 'type': 'ExplicitComment',
        'raw': '@Comment{This is another comment}',
        'line': 60, 'comment': 'This is another comment'
    },
])
def test_comments(expected: Dict[str, any]) -> None:
    library = _split()
    comments = library.comments
    assert len(comments) == 3

    # Raise KeyError if not found
    tested_comment = comments[expected['comment_position']]
    # Test parsed comment
    assert tested_comment is not None
    assert expected['type'] in str(type(tested_comment))
    assert tested_comment.raw == expected['raw']
    assert tested_comment.start_line == expected['line']
    assert tested_comment.comment == expected['comment']
    # Make sure position in overall blocks matches
    assert library.blocks[expected['position']] == tested_comment
    # Make sure position in comment blocks matches
    assert library.comments[expected['comment_position']] == tested_comment


