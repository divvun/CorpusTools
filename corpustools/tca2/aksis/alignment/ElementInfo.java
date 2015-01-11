package aksis.alignment;

import java.util.List;
import java.util.ArrayList;

/**
 * information about an alignable element.
 * this is information that is used when comparing elements from the texts. ¤¤¤
 */
class ElementInfo {

	// ###### skulle den hatt en referanse til selve elementet?
	// length of text content in characters
	int length = 0;
	// number of words
	int numWords = 0;
	// array of all the words
	String[] words;
	// list of anchor word hits,
	// a hit being a 2 element list, consisting of
	// - a reference to an entry (line) in an anchor word file,
	// - a copy of the matching word.
	// the anchor word entry reference is an Integer - a line number, starting with 0 (?)
	AnchorWordHits anchorWordHits = new AnchorWordHits();
	// list of proper names ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ hva hvis samme navn flere ganger - m i den ene teksten og n i den andre? kan gi for mange poeng - m x n. bør vel heller gi max(m, n) poeng.
	List properNames = new ArrayList();
	// a string of all the "scoring special characters" in the element, as many times as the occur, in original order
	String scoringCharacters = "";

	int elementNumber;   // ###nyttig eller unødvendig? 2006-04-05

	/**
	 *
	 */
	public ElementInfo() {
		//
	}

	/**
	 *

	 */
	//public ElementInfo(AlignmentModel model, String text, int t) {
	public ElementInfo(AlignmentModel model, String text, int t, int elementNumber) {   // 2006-04-05

		//
		this.elementNumber = elementNumber;   // ###nyttig eller unødvendig? 2006-04-05
		length = text.length();
		//System.out.println("ElementInfo constructor");
		//System.out.println("text = " + text);
		//System.out.println("length = " + length);
		// ¤¤¤ foreløpig.
		// deler ved whitespace, og skreller noen spesialtegn av ordene
		// ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ blir det tomme ord også? ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ SJEKK!
		// words have space between them, and may be flanked by special characters
		//String specialCharacters = ".,;:()'" + '"';
		//String specialCharactersPattern = Pattern.quote(specialCharacters);   // Pattern.quote is JDK 1.5
		//System.out.println("specialCharacters=" + specialCharacters);
		//System.out.println("specialCharactersPattern=" + specialCharactersPattern);
		//specialCharactersPattern = "[" + "\\s" + ".,;:()'" + '"' + "]";   // §§§§§§§§§§§§§§§§§§midlertidig
		//words = text.split("[\\s.,;:()]*\\s[\\s.,;:()]*");
		//String specialCharacters = ".,;:?!&^(){}[]'" + '"';
		String specialCharacters = model.getSpecialCharacters();
		//String[] difficultCharacters = { "]", "\\", "^", "-" };
		// build pattern. first a 'character class' ('grouping', 'set', i.e, []-bracketed regex thingie)
		// with all special, characters and whitespace
		String specialCharactersClass = "[\\s";
		for (int i=0; i < specialCharacters.length(); i++) {
			//specialCharactersClass += "\\" + specialCharacters.substring(i, i);   // ??? får ikke tak i verdi fra specialCharacters.substring(i, i). nullstreng
			specialCharactersClass += "\\" + String.valueOf(specialCharacters.charAt(i));   // escape all of them, to be certain that the difficult ones are escaped: [\^-
		}
		specialCharactersClass += "]";
		// then a pattern to split the string into words.
		// it is assumed words are separated by whitespace,
		// possibly with special characters sticking to the ends.
		// the splitting will split into words
		// and remove the leading/trailing special characters from the words
		String specialCharactersPattern = specialCharactersClass + "*\\s" + specialCharactersClass + "*";
		//System.out.println("specialCharactersPattern = " + specialCharactersPattern);
		//for (int i=0; i < specialCharacters.length(); i++) {
		//	if (difficultCharacters.
		//// force metacharacters to be treated as ordinary characters by enclosing them within \Q and \E
		//String specialCharactersPattern = "[" + "\\s" + "\\Q" + specialCharacters + "\\E" + "]*";
		//// when splitting surround the text with spaces.
		//// this will cause the splitting pattern to do its special character stripping work
		//// not just between the words, but also before and after the first and last word
		//String[] tempWords = (" " + text + " ").split(specialCharactersPattern + "\\s" + specialCharactersPattern);
		//String[] tempWords = (" " + text + " ").split("[\\s\\Q.,;:()'\\E]*\\s[\\s\\Q.,;:()'\\E]*");  // får ikke \Q...\E til å funke
		//String[] tempWords = (" " + text + " ").split("[\\s\\.\\,\\;\\:\\(\\)\\'\\""]*\\s[\\s\\.\\,\\;\\:\\(\\)\\'\\"'+"]*");   // dette funker
		String[] tempWords = (" " + text + " ").split(specialCharactersPattern);
		// ¤¤¤ <http://www.regular-expressions.info/charclass.html> Note that the only special characters or metacharacters inside a character class are the closing bracket (]), the backslash (\), the caret (^) and the hyphen (-).
		// ¤¤¤ hva med &? java docs sier && har spesiell betydning, men det er kanskje etter ]?
		// remove that extra element that was produced because of the leading space
		numWords = tempWords.length - 1;
		words = new String[numWords];
		System.arraycopy(tempWords, 1, words, 0, numWords);
		tempWords = null;
		//System.out.print("# = " + numWords + ":");
		for (int w=0; w<words.length; w++) {
			//System.out.print(" " + words[w]);
		}
		//System.out.println("");
		//anchorWordHits = model.anchorWordList.getAnchorWordHits(words, t);   // ¤¤¤ hmmm. er det sikkert at ankerordlisten står rette veien? tenk om gui har engelsk-norsk, og ankerordlisten har norsk-engelsk?
		anchorWordHits = model.anchorWordList.getAnchorWordHits(words, t, elementNumber);   // ¤¤¤ hmmm. er det sikkert at ankerordlisten står rette veien? tenk om gui har engelsk-norsk, og ankerordlisten har norsk-engelsk?   // 2006-04-05
		//System.out.println(">>> ElementInfo constructor. anchorWordHits = " + anchorWordHits);
		// ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ getProperNames() hører vel ikke hjemme i AnchorWordList, men hvor skal jeg ha den?
		properNames = model.anchorWordList.getProperNames(words);
		// ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ tilsvarende
		scoringCharacters = model.anchorWordList.getScoringCharacters(text);
		//System.out.println("ElementInfo constructor. scoringCharacters = " + scoringCharacters);

	}

	// ### for debuggingsformål

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

