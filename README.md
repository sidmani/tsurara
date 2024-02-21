# tsurara

1. `pip install -r requirements.txt`
2. `python -m unidic download` (downloads a 500MB dictionary file)
3. `python -m tsurara review -i subtitle_file.srt -o output_file.csv`

This will:

- parse the subtitle file
- tokenize the Japanese text into words
- filter out words that you probably don't care about (particles, proper nouns, suffixes, etc.)
- sort the words in descending order of frequency of appearance in Wikipedia
- drop you into the main loop that iterates over words

While in the loop, tsurara incrementally saves data to a file called `.tsurara.json` in your home directory (which you don't need to touch) and your specified output csv. Even if you exit at any point, your progress until that point is saved.

In the main loop, you have the following options:

- known: mark a word as known forever. you will never see it again
- reveal meaning: show meaning of the word and redisplay the menu. if it revealed the meaning by default it would be hard to tell if you knew the word
- add: add the word to your output file (there are a few submenus to choose the reading and definition). this also marks the word as known
- skip: do nothing. go to next word
- ignore: mark a word as ignored forever. this is does more or less the same thing as known but is separate because I'm going to add an option to clear ignored words later
- quit: exit immediately. your progress excluding the current word is saved.

The first letter of each option corresponds to its keyboard shortcut.

The advantage of this tool is that as you process more files, your known words list will grow. Since words are sorted by descending frequency, loading a new file will show you the most common words you don't know. So even if you don't go through all the words in a file you're spending your time optimally.
