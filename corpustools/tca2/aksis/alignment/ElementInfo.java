package aksis.alignment;

import java.util.List;
import java.util.ArrayList;

/**
 * information about an alignable element.
 * this is information that is used when comparing elements from the texts. ¤¤¤
 */
class ElementInfo {

	int length = 0;
	int numWords = 0;
	String[] words;
	AnchorWordHits anchorWordHits = new AnchorWordHits();
	List<String> properNames = new ArrayList<String>();
	String scoringCharacters = "";
	int elementNumber;

	public ElementInfo() {
	}

	public ElementInfo(AlignmentModel model, String text, int t, int elementNumber) {   
		this.elementNumber = elementNumber;
		length = text.length();
		String specialCharacters = model.getSpecialCharacters();
		String specialCharactersClass = "[\\s";
		for (int i=0; i < specialCharacters.length(); i++) {
			specialCharactersClass += "\\" + String.valueOf(specialCharacters.charAt(i));
		}
		specialCharactersClass += "]";
		String specialCharactersPattern = specialCharactersClass + "*\\s" + specialCharactersClass + "*";
		String[] tempWords = (" " + text + " ").split(specialCharactersPattern);
		numWords = tempWords.length - 1;
		words = new String[numWords];
		System.arraycopy(tempWords, 1, words, 0, numWords);
		tempWords = null;
		anchorWordHits = model.anchorWordList.getAnchorWordHits(words, t, elementNumber);
		properNames = model.anchorWordList.getProperNames(words);
		scoringCharacters = model.anchorWordList.getScoringCharacters(text);
	}

	public String toString() {

		StringBuffer ret = new StringBuffer();
		ret.append("# chars = " + length);
		ret.append("; ");
		ret.append("# words = " + numWords);
		ret.append("; ");
		ret.append("words = {");
		for (int i=0; i < words.length; i++) {
			if (i > 0) { ret.append(", "); }
			ret.append(words[i]);
		}
		ret.append("}; ");
		ret.append("anchor word hits = " + anchorWordHits);
		ret.append("; ");
		ret.append("proper names = " + properNames);
		return new String(ret);

	}

}

