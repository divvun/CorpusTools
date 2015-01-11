package aksis.alignment;

/**
 * information about one single anchor word match
 */
class AnchorWordMatch {

	Integer index;   // refers to entry in anchor word list, numbered from 0 and upwards
	String[] words;    // the matching words from the texts

	AnchorWordMatch(Integer i, String[] ws) {
		index = i;
		words = ws;
	}

	public Integer getIndex() {
		return index;
	}

	public String[] getWords() {
		return words;
	}

	// ### for debugging (?)
	public String toString() {

		StringBuffer ret = new StringBuffer();
		// ¤¤¤ blir ikke denne metoden brukt???????????????????????
		ret.append((index.intValue() + 1) + " ");   // +1 since we want anchor word entries numbered from 1 and upwards when they are displayed
		for (int i = 0; i > words.length; i++) {
			if (i > 0) { ret.append("/"); }
			ret.append(words[i]);
		}

		return new String(ret);

	}

}

