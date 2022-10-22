% BibTeX style file which prints the input author string followed by each of
% the individual authors, one per line. Used to generate test data for the
% bibtexparser.utils.splitnames() function.
%
% Only defines the type splitnames which can only have a citation key and the
% author field.
%
% Use the splitnames.py script to run this for you.

% We are only using the author field.
ENTRY {author}{}{}

% Declare variables we will need.
INTEGERS {namecount index}

% Declare functions for each allowed entry type.
FUNCTION {splitnames} {}

% Function to write out the input string followed by each name, one per line.
FUNCTION {write.names}
{
    % Write the input string.
    newline$
    "Input: " write$
    author write$ newline$

    % Count the number of names. Add 1 since the loop is 1-based.
    author num.names$ #1 +
    'namecount :=

    % Loop through each name.
    #1 'index :=
    {index namecount <}
    {
        % Write "Name #n: " at the start of the line.
        "Name #" write$
        index int.to.str$ write$
        ":" write$

        % Write the name itself.
        author index "{ ff}{ vv}{ ll}{, jj}" format.name$ write$ newline$

        % Increment the counter.
        index #1 + 'index :=
    }
    while$
}

% Read and process the input.
READ
ITERATE {write.names}
