/*
 * AnchorWordList.java
 *
 * ...
 * ...
 * ...
 */

package aksis.alignment;

import javax.swing.JOptionPane;
import javax.swing.JTextArea;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.regex.Pattern;


import java.io.File;
import java.io.FileReader;
import java.io.BufferedReader;
import java.io.IOException;


/**
 * anchor word list.
 * list, with each element a AnchorWordListEntry.
 */
class AnchorWordList {

	java.util.List<AnchorWordListEntry> entries = new ArrayList<AnchorWordListEntry>();   // explicit to avoid ambiguousness

	AlignmentModel model;

	AnchorWordList(AlignmentModel model) {
		this.model = model;
	}

	/*
	 * Added by boerre
	 */
	public void loadFromFile(File fromFile) {
		entries.clear();

		boolean ok = true;
		try {
			BufferedReader in = new BufferedReader(new FileReader(fromFile));
			String str;
			while ((str = in.readLine()) != null) {
				try {
					
					entries.add(new AnchorWordListEntry(str.trim()));
				} catch (Exception e) {
					System.err.println("Error in anchor word entry: " + e.getMessage());
					ok = false;
					break;
				}
			}
		} catch (IOException e) {
		}

		if (!ok) {
			System.out.println("Error occurred. clear list again");
			entries.clear();   // ¤¤¤ er ikke dette bedre?
		}
	}		

	public void load(ArrayList<String> lines) {

		//System.out.println("AnchorWordList sin load()");
		//System.out.println("lines.size() = " + lines.size());
		// clear list
		//java.util.List entries = new ArrayList(); denne førte til at model sin anchorWordList likevel ikke ble satt. har ikke tenkt gjennom hvorfor
		entries.clear();

		// load list
		boolean ok = true;
		Iterator<String> it = lines.iterator();
		while (it.hasNext()) {
			String line = ((String)(it.next())).trim();
			if (line.length() > 0) {
				//System.out.println("line='"+line+"'");
				try {
					entries.add(new AnchorWordListEntry(line));
				} catch (Exception e) {
					System.err.println("Error in anchor word entry: " + e.getMessage());
					JOptionPane.showMessageDialog(
						null,
						"Error in anchor word entry: " + e.getMessage(),
						"Error in anchor word entry",
						JOptionPane.ERROR_MESSAGE
					);
					ok = false;
					break;
				}
			}
			//System.out.println("entries.size() = " + entries.size());
		}

		if (!ok) {
			// error occurred. clear list again
			System.out.println("Error occurred. clear list again");
			//entries = new ArrayList();
			entries.clear();   // ¤¤¤ er ikke dette bedre?
		}

	}

	public void display(JTextArea content) {

		if (entries != null) {

			Iterator<AnchorWordListEntry> eIt = entries.iterator();
			while (eIt.hasNext()) {

				//System.out.println("neste entry");

				StringBuffer anchorWordListEntryText = new StringBuffer("");
				AnchorWordListEntry anchorWordListEntry = (AnchorWordListEntry)eIt.next();
				for (int t=0; t<Alignment.NUM_FILES; t++) {
					//System.out.println("t=" + t);
					if (t > 0) {
						//System.out.println("append /");
						anchorWordListEntryText.append("/");   // ### sett konstanter et felles sted
					}
					java.util.List synonyms = anchorWordListEntry.language[t];
					Iterator sIt = synonyms.iterator();
					boolean first = true;
					//System.out.println("antall fraser=" + synonyms.size());
					while (sIt.hasNext()) {
						//System.out.println("neste frase");
						if (first) {
							first = false;
						} else {
							//System.out.println("append ,");
							anchorWordListEntryText.append(",");   // ### sett konstanter et felles sted
						}
						//word = (String)wIt.next();
						//anchorWordListEntryText.append(word);
						java.util.List<String> phrase = (java.util.List)sIt.next();
						Iterator<String> wIt = phrase.iterator();
						boolean firstW = true;
						//System.out.println("antall ord=" + phrase.size());
						while (wIt.hasNext()) {
							//System.out.println("neste ord");
							if (firstW) {
								firstW = false;
							} else {
								//System.out.println("append space");
								anchorWordListEntryText.append(" ");   // ### sett konstanter et felles sted
							}
							String word = (String)wIt.next();
							//System.out.println("append word");
							anchorWordListEntryText.append(word);
						}
					}
				}

				content.append(anchorWordListEntryText + "\n");

			}

		}
	}

	public AnchorWordListEntry getEntry(int i) {

		return (AnchorWordListEntry)entries.get(i);

	}

	/**
	 * takes as the first argument an array of words.
	 * these are all the words from one alignable element, in original order.
	 * searches anchor word list for matches with these words.
	 * the t-th side of the anchor word list is searched (0=left, 1=right).
	 * returns hits (matches) as list of numbers. ### etc
	 * each number is the number of an item (i.e, line???) ### entry in the anchor word list.
	 */
	// ### 'get' as in 'compute'
	//public AnchorWordHits getAnchorWordHits(String[] words, int t) {
	public AnchorWordHits getAnchorWordHits(String[] words, int t, int elementNumber) {   // 2006-04-05
		//System.out.println(">>>>>>>>>>>getAnchorWordHits<<<<<<<<<<<<");
		AnchorWordHits ret = new AnchorWordHits();
		//
		Iterator<AnchorWordListEntry> aIt = this.entries.iterator();
		int anchorWordEntryCount = 0;
		while (aIt.hasNext()) {
			//System.out.println("anchorWordEntryCount = " + anchorWordEntryCount);
			//java.util.List synonyms = ((AnchorWordListEntry)(aIt.next())).language[t];
			AnchorWordListEntry entry = (AnchorWordListEntry)(aIt.next());
			java.util.List synonyms = (java.util.List)(entry.language[t]);
			Iterator sIt = synonyms.iterator();
			while (sIt.hasNext()) {
				java.util.List<Pattern> anchorPhrase = (java.util.List)sIt.next();
				//System.out.println("anchorPhrase = " + anchorPhrase);
				for (int w=0; w<words.length - anchorPhrase.size() + 1; w++) {
					boolean success = true;
					// loop over word in phrase
					StringBuffer matchingPhrase = new StringBuffer();   // the actual phrase occurring in the text
					for (int w2=0; w2<anchorPhrase.size(); w2++) {
						String word = words[w+w2];
						Pattern anchorWord = (Pattern)(anchorPhrase.get(w2));
						//System.out.println("word = " + word);
						//if (anchorWord == word) {
						//if (anchorWord.equals(word)) {
						//if (anchorWord.equalsIgnoreCase(word)) {   // ### eller skal det være noe mer sofistikert? alfa = Alfa, men ikke ALFA? alfa = Alfa, men kun hvis Alfa er første ord i setningen?
						if (SimilarityUtils.anchorMatch(anchorWord, word)) {
							if (w2 > 0) matchingPhrase.append(" ");
							matchingPhrase.append(word);
						} else {
							success = false;
							break;
						}
					}
					if (success) {
						//System.out.println("match!");
						//System.out.println("match. matchingPhrase = " + matchingPhrase);
						//AnchorWordHit hit = new AnchorWordHit(new Integer(anchorWordEntryCount), new String(matchingPhrase));
						AnchorWordHit hit = new AnchorWordHit(new Integer(anchorWordEntryCount), elementNumber, w, new String(matchingPhrase));   // 2006-04-05
						ret.add(hit);
					}
				}
			}
			anchorWordEntryCount++;
		}
		return ret;
	}

	// ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ hører vel ikke hjemme her, men hvor skal jeg ha den?

	/**
	 * takes array.
	 * extracts words starting with uppercase letter.
	 * returns as list.
	 */
	public java.util.List getProperNames(String[] words) {
		//System.out.println("getProperNames. words.length=" + words.length);
		java.util.List ret = new ArrayList();
		for (int w=0; w<words.length; w++) {
			//System.out.println("words["+w+"]=" + words[w]);
			String word = words[w];
			if (word.length() > 0) {
				if (Character.isUpperCase(word.charAt(0))) {   // Character.isUppercase() ? cast med (char), nei (Character) ?
					ret.add(word);
				}
			}
		}
		return ret;
	}

	/**
	 * takes the text and extracts all the scoring characters.
	 * returns as a string with all the characters (occurences) in original order
	 */
	// ### to metoder med samme navn ###
	public String getScoringCharacters(String text) {
		String scoringCharacters = model.getScoringCharacters();
		String ret = "";
		//System.out.println("getScoringCharacters(). text = " + text);
		//System.out.println("getScoringCharacters(). scoringCharacters = " + scoringCharacters);
		for (int i=0; i<text.length(); i++) {
			if (scoringCharacters.indexOf(text.substring(i, i+1)) >= 0) {
				ret += text.substring(i, i+1);
			}
		}
		//System.out.println("getScoringCharacters() returns " + ret);
		return ret;
	}

}

