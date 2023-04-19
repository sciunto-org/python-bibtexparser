import logging
import logging.config
import io

logger = logging.getLogger(__name__)

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s %(funcName)s:%(lineno)d: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'DEBUG',
            'formatter': 'standard',
            'class':'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'formatter': 'standard',
            'propagate': True
        }
    }
})


if __name__ == '__main__':
    bibtex_source = """@ARTICLE{Cesar2013,
      author = {Jean César},
      title = {An amazing title},
      year = {2013},
      month = {1},
      volume = {12},
      pages = {12--23},
      journal = {Nice Journal},
      abstract = {This is an abstract. This line should be long enough to test
    	 multilines...},
      comments = {A comment},
      keywords = {keyword1, keyword2},
    }
    """

    from bibtexparser.bparser import BibTexParser

    with io.StringIO(bibtex_source) as f:
        bp = BibTexParser(f.read())
        print(bp.get_entry_list())
