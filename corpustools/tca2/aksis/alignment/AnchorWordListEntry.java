package aksis.alignment;

import java.util.ArrayList;
import java.util.regex.Pattern;

/**
 * entry in anchor word list.
 * array with one element for each language.
 * each language element is a list of arrays.
 * each array contains a phrase with one word per element.
 * most phrases will have just one word
 */
class AnchorWordListEntry {

	// for hvert språk en liste av "synonymer"
	java.util.List[] language = new ArrayList[Alignment.NUM_FILES];   // ¤¤¤ skal vel heller være 2

	public AnchorWordListEntry(String anchorWordListEntryText) throws Exception {   // anchorWordListEntryText syntax must be e.g "en,et/one" with delimiters "/" and "'" and no whitespace whatsoever

		if (anchorWordListEntryText.length() > 0) {

			String[] data = anchorWordListEntryText.split("/");   // split entry into array of data for each text/language

			if (data.length < Alignment.NUM_FILES) {
				throw new Exception("No slash: " + anchorWordListEntryText);   // §§§
			} else if (data.length > Alignment.NUM_FILES) {
				throw new Exception("Too many slashes: " + anchorWordListEntryText);   // §§§
			}

			for (int t=0; t<Alignment.NUM_FILES; t++) {
				language[t] = new ArrayList<ArrayList<Pattern>>();
				String[] syns = data[t].split(",");   // split data for one language into array of "synonyms". each synonym can be a phrase
				for (int ph=0; ph<syns.length; ph++) {
					String[] words = syns[ph].split(" ");  // split phrase into array of words. in practice most phrases will contain just one word
					java.util.List<Pattern> phrase = new ArrayList<Pattern>();   // array to contain one phrase, with one word per element
					for (int w=0; w<words.length; w++) {
						String word = words[w].trim();
						if (!(word.equals(""))) {
							phrase.add(makeCompiledPattern(word));
						}
					}
					if (phrase.size() > 0) {
						language[t].add(phrase);
					}
				}
			}
		}
	}
	
	Pattern makeCompiledPattern(String anchorWord) {
        // make a proper regular expression from the anchor word
        String pattern = "^" + anchorWord.replaceAll("[*]", ".*") + "$";
        return (Pattern.compile(pattern, Pattern.CASE_INSENSITIVE + Pattern.UNICODE_CASE));
    }
}

