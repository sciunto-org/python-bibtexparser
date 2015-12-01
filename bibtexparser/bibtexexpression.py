import pyparsing as pp


# General helpers

def strip_after_new_lines(s):
    lines = s.splitlines()
    if len(lines) > 1:
        lines = [lines[0]] + [l.lstrip() for l in lines[1:]]
    return '\n'.join(lines)


def add_logger_parse_action(expr, log_func):
    def action(s, l, t):
        log_func("Found {}: {}".format(expr.resultsName, t))
    expr.addParseAction(action)


# Parse action helpers

def first_token(s, l, t):
    # TODO Handle this case correctly!
    assert(len(t) == 1)
    return t[0]


def remove_trailing_newlines(s, l, t):
    if t[0]:
        return t[0].rstrip('\n')


def remove_braces(s, l, t):
    if len(t[0]) < 1:
        return ''
    else:
        start = 1 if t[0][0] == '{' else 0
        end = -1 if t[0][-1] == '}' else None
        return t[0][start:end]


def field_to_pair(s, l, t):
    """
    Looks for parsed element named 'Field'.
    :returns: (name, value).
    """
    f = t.get('Field')
    # Not sure it is desirable here to strip but it is for conformance
    # to previous implementation
    return (f.get('FieldName'),
            strip_after_new_lines(f.get('Value')))


# Expressions helpers

def in_braces_or_pars(exp):
    """
    exp -> (exp)|{exp}
    """
    return ((pp.Suppress('{') + exp + pp.Suppress('}')) |
            (pp.Suppress('(') + exp + pp.Suppress(')')))


class BibtexExpression(object):
    """Gives access to pyparsing expressions.

    Attributes are pyparsing expressions for the following elements:
        main_expression: the bibtex file
        string_def: a string definition
        preamble_decl: a preamble declaration
        explicit_comment: an explicit comment
        entry: an entry definition
        implicit_comment: an implicit comment
    """

    ParseException = pp.ParseException

    def __init__(self):
        string_def_start = pp.CaselessKeyword("@string")
        preamble_start = pp.CaselessKeyword("@preamble")
        comment_line_start = pp.CaselessKeyword('@comment')

        # Values

        integer = pp.Word(pp.nums)('Integer')

        braced_value_content = pp.CharsNotIn('{}')
        braced_value = pp.Forward()
        braced_value <<= pp.originalTextFor(
            '{' + pp.ZeroOrMore(braced_value | braced_value_content) + '}'
            )('BracedValue')
        braced_value.setParseAction(remove_braces)
        # TODO add ignore for "\}" and "\{" ?
        # TODO @ are not parsed by bibtex in braces

        brace_in_quoted = pp.nestedExpr('{', '}')
        text_in_quoted = pp.Word(pp.printables, excludeChars='"{}')
        quoted_value = pp.originalTextFor(
            '"' +
            pp.ZeroOrMore(text_in_quoted | brace_in_quoted) +
            '"')('QuotedValue')
        quoted_value.addParseAction(pp.removeQuotes)
        # TODO Make sure that content is escaped with quotes when contains '@'

        string_name = pp.Word(pp.alphanums + '_')('StringName')
        self.set_string_name_parse_action(lambda s, l, t: None)
        string_name.addParseAction(self._string_name_parse_action)

        string_expr = pp.delimitedList(
            (quoted_value | braced_value | string_name), delim='#'
            )('StringExpression')
        self.set_string_expression_parse_action(lambda s, l, t: None)
        string_expr.addParseAction(self._string_expr_parse_action)

        value = (integer | string_expr)('Value')

        # Entries

        entry_type = (pp.Suppress('@') + pp.Word(pp.alphas))('EntryType')
        entry_type.setParseAction(first_token)

        key = pp.SkipTo(',')('Key')  # Exclude @',\#}{~%
        key.setParseAction(lambda s, l, t: first_token(s, l, t).strip())

        field_name = pp.Word(pp.alphas)('FieldName')
        field_name.setParseAction(first_token)
        field = pp.Group(field_name + pp.Suppress('=') + value)('Field')

        field.setParseAction(field_to_pair)

        field_list = (pp.delimitedList(field) + pp.Suppress(pp.Optional(','))
                      )('Fields')
        field_list.setParseAction(
            lambda s, l, t: {k: v for (k, v) in reversed(t.get('Fields'))})

        self.entry = (entry_type +
                      in_braces_or_pars(key + pp.Suppress(',') + field_list)
                      )('Entry')

        # Other stuff
        not_an_implicit_comment = (pp.LineStart() + pp.Literal('@')
                                   ) | pp.stringEnd()
        self.explicit_comment = (
            pp.Suppress(comment_line_start) +
            pp.originalTextFor(pp.SkipTo(not_an_implicit_comment),
                               asString=True))('ExplicitComment')
        self.explicit_comment.addParseAction(remove_trailing_newlines)
        self.explicit_comment.addParseAction(remove_braces)
        # Previous implementation included comment until next '}'.
        # This is however not inline with bibtex behavior that is to only
        # ignore until EOL. Brace stipping is arbitrary here but avoids
        # duplication on bibtex write.

        # Empty implicit_comments lead to infinite loop of zeroOrMore
        def mustNotBeEmpty(t):
            if not t[0]:
                raise pp.ParseException("Match must not be empty.")

        self.implicit_comment = pp.originalTextFor(
            pp.SkipTo(not_an_implicit_comment).setParseAction(mustNotBeEmpty),
            asString=True)('ImplicitComment')
        self.implicit_comment.addParseAction(remove_trailing_newlines)

        self.string_def = (pp.Suppress(string_def_start) + in_braces_or_pars(
            string_name +
            pp.Suppress('=') +
            string_expr('StringValue')
            ))('StringDefinition')
        self.preamble_decl = (pp.Suppress(preamble_start) +
                              in_braces_or_pars(value))('PreambleDeclaration')

        # Main bibtex expression
        self.main_expression = pp.ZeroOrMore(
                self.string_def |
                self.preamble_decl |
                self.explicit_comment |
                self.entry |
                self.implicit_comment)

    def add_log_function(self, log_fun):
        for e in [self.entry,
                  self.implicit_comment,
                  self.explicit_comment,
                  self.preamble_decl,
                  self.string_def]:
            add_logger_parse_action(e, log_fun)

    def set_string_name_parse_action(self, fun):
        """Set the paseAction for string name expression.

        Note: for some reason pyparsing duplicates the string_name
        expression so setting its parseAction a posteriori has no effect
        in the context of a string expression. This is why this function
        should be used instead.
        """
        self._string_name_parse_action_fun = fun

    def _string_name_parse_action(self, s, l, t):
        return self._string_name_parse_action_fun(s, l, t)

    def set_string_expression_parse_action(self, fun):
        """Set the paseAction for string_expression expression.

        Note: see set_string_name_parse_action.
        """
        self._string_expr_parse_action_fun = fun

    def _string_expr_parse_action(self, s, l, t):
        return self._string_expr_parse_action_fun(s, l, t)

    def parseFile(self, file_obj):
        return self.main_expression.parseFile(file_obj, parseAll=True)
