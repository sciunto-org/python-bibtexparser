% BibTeX style file which prints the input author string followed by the
% components (First, von, Last, jr) of the name, one component per line.  Used
% to generate test data for the bibtexparser.utils.parsename() function.
%
% Only defines the type parsename which can only have a citation key and the
% author field.
%
% Use the parsename.py script to run this for you.

% We are only using the author field.
ENTRY {author}{}{}

% Declare variables we will need.
INTEGERS {namecount index}

% Declare functions for each allowed entry type.
FUNCTION {parsename} {}

% Function to write out the input string followed by each name, one per line.
FUNCTION {parse.names}
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
        % Write the parts on separate lines.
        "First: " write$ author index "{ff}" format.name$ write$ newline$
        "  von: " write$ author index "{vv}" format.name$ write$ newline$
        " Last: " write$ author index "{ll}" format.name$ write$ newline$
        "   jr: " write$ author index "{jj}" format.name$ write$ newline$

        % Increment the counter.
        index #1 + 'index :=
    }
    while$
}

% Read and process the input.
READ
ITERATE {parse.names}
