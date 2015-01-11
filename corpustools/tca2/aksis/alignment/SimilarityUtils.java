/*
 * SimilarityUtils.java
 *
 * ...
 * ...
 * ...
 */

package aksis.alignment;

//
import java.util.*;
//import java.lang.Math.*;
import java.util.regex.*;

class SimilarityUtils {

	//public static float dice(String word1, String word2) {
	public static boolean diceMatch(String word1, String word2, float diceMinCountingScore) {   // 2006-08-09

		// ¤¤¤ this function does case sensitive comparisons
		// ### not anymore

		// ...
		//System.out.println("ankommer dice(). word1=" + word1 + " word2=" + word2);

		int i;
		String word1LowerCase = word1.toLowerCase();
		String word2LowerCase = word2.toLowerCase();

		// find all unique bigrams in first word

		Hashtable uniqueBigrams1 = new Hashtable();
		int countBigrams1;
		for (i = 0; i < word1LowerCase.length() - 1; i++) {
			uniqueBigrams1.put(word1LowerCase.substring(i, i+2), new Integer(1));
		}
		countBigrams1 = uniqueBigrams1.size();

		// find all unique bigrams in second word

		Hashtable uniqueBigrams2 = new Hashtable();
		int countBigrams2;
		for (i = 0; i < word2LowerCase.length() - 1; i++) {
			uniqueBigrams2.put(word2LowerCase.substring(i, i+2), new Integer(1));
		}
		countBigrams2 = uniqueBigrams2.size();

		// count all shared bigrams

		////Hashtable sharedBigrams = new Hashtable();
		int countSharedBigrams = 0;
		for (Enumeration e = uniqueBigrams1.keys(); e.hasMoreElements();) {
			if (uniqueBigrams2.containsKey(e.nextElement())) {
				countSharedBigrams++;
			}
		}
		//System.out.println("dice() forts. countBigrams=" + countBigrams1 + " countBigrams2=" + countBigrams2 + " countSharedBigrams=" + countSharedBigrams);

		// calculate dice score

		float diceScore;
		if ((countBigrams1 == 0) || (countBigrams2 == 0)) {
			diceScore = 0;
		} else {
			////diceScore = countSharedBigrams / (countBigrams1 + countBigrams2); ?????????????
			diceScore = (2 * (float)countSharedBigrams) / (countBigrams1 + countBigrams2);   // ?????????????
		}
		//System.out.println("dice() forts. diceScore=" + diceScore);

		//

		// decide if scores are high enough   // 2006-08-09

		//return diceScore;
		return (diceScore >= diceMinCountingScore);   // 2006-08-09

	}

	//#######den er jo helt feil. den ser ikke på hvordan hvert av ordene i frasen matcher.
	//#######aha. kanskje jeg tenkte at kallende rutine skulle gjøre dette, men glemte å ordne det der?
	//// 2006-04-18
	//
	//// ### burde disse (metoden over og denne metoden)
	//
	//// vært slått sammen? eller kode skilt ut i felles metoder?
	//
	//public static float dice(String word1, String word2, String type) {
	//
	//	String phrase;
	//	String word;
	//	if (type == "2-1") {
	//		phrase = word1;
	//		word   = word2;
	//	} else if (type == "1-2") {
	//		word   = word1;
	//		phrase = word2;
	//	} else {
	//		// ### program error
	//		return -1.0f;
	//	}
	//	//System.out.print("phrase=" + phrase);
	//	//System.out.print("word=" + word);
	//
	//	int i;
	//	String wordLowerCase   = word.toLowerCase();
	//	String phraseLowerCase = phrase.toLowerCase();
	//
	//	// find all unique bigrams in word
	//
	//	Hashtable uniqueBigramsInWord = new Hashtable();
	//	int countBigramsInWord;
	//	for (i = 0; i < wordLowerCase.length() - 1; i++) {
	//		uniqueBigramsInWord.put(wordLowerCase.substring(i, i+2), new Integer(1));
	//	}
	//	countBigramsInWord = uniqueBigramsInWord.size();
	//
	//	// find all unique bigrams in phrase
	//
	//	Hashtable uniqueBigramsInPhrase = new Hashtable();
	//	int countBigramsInPhrase;
	//	for (i = 0; i < phraseLowerCase.length() - 1; i++) {
	//		uniqueBigramsInPhrase.put(phraseLowerCase.substring(i, i+2), new Integer(1));
	//	}
	//	countBigramsInPhrase = uniqueBigramsInPhrase.size();
	//
	//	// count all shared bigrams
	//
	//	int countSharedBigrams = 0;
	//	for (Enumeration e = uniqueBigramsInWord.keys(); e.hasMoreElements();) {
	//		if (uniqueBigramsInPhrase.containsKey(e.nextElement())) {
	//			countSharedBigrams++;
	//		}
	//	}
	//
	//	// calculate dice score
	//
	//	float diceScore;
	//	if ((countBigramsInWord == 0) || (countBigramsInPhrase == 0)) {
	//		diceScore = 0;
	//	} else {
	//		diceScore = (float)countSharedBigrams / countBigramsInWord;   // ????????????? ##############
	//		// which is the same as
	//		// diceScore = (2 * (float)countSharedBigrams) / (countBigramsInWord * 2);
	//		// where we sort of pretend the phrase is of the same length as the word
	//	}
	//
	//	return diceScore;
	//
	//}
	//// end 2006-04-18

	// 2006-08-09


	public static boolean diceMatch(String wordA, String wordB, String wordC, String type, float diceMinCountingScore) {

		// if type = "2-1" the phrase wordA + wordB is to be compared with the word   wordC        .
		// if type = "1-2" the word   wordA         is to be compared with the phrase wordB + wordC.

		String phraseWord1, phraseWord2;
		String word;
		String phrase;
		if (type == "2-1") {
			phraseWord1 = wordA;
			phraseWord2 = wordB;
			word        = wordC;
		} else if (type == "1-2") {
			word        = wordA;
			phraseWord1 = wordB;
			phraseWord2 = wordC;
		} else {
			// ### program error
			//return -1.0f;
			return false;   // 2006-08-09
		}
		//System.out.print("phraseWord1=" + phraseWord1);
		//System.out.print("phraseWord2=" + phraseWord2);
		//System.out.print("word="        + word       );
		phrase = phraseWord1 + phraseWord2;

		int i;
		String wordLowerCase        = word.toLowerCase();
		String phraseWord1LowerCase = phraseWord1.toLowerCase();
		String phraseWord2LowerCase = phraseWord2.toLowerCase();
		String phraseLowerCase      = phraseWord1LowerCase + phraseWord2LowerCase;

		// find all unique bigrams in word

		Hashtable uniqueBigramsInWord = new Hashtable();
		int countBigramsInWord;
		for (i = 0; i < wordLowerCase.length() - 1; i++) {
			uniqueBigramsInWord.put(wordLowerCase.substring(i, i+2), new Integer(1));
		}
		countBigramsInWord = uniqueBigramsInWord.size();

		// find all unique bigrams in phrase's 1st word

		Hashtable uniqueBigramsInPhraseWord1 = new Hashtable();
		int countBigramsInPhraseWord1;
		for (i = 0; i < phraseWord1LowerCase.length() - 1; i++) {
			uniqueBigramsInPhraseWord1.put(phraseWord1LowerCase.substring(i, i+2), new Integer(1));
		}
		countBigramsInPhraseWord1 = uniqueBigramsInPhraseWord1.size();

		// count all shared bigrams

		int countSharedBigrams1 = 0;
		for (Enumeration e = uniqueBigramsInWord.keys(); e.hasMoreElements();) {
			if (uniqueBigramsInPhraseWord1.containsKey(e.nextElement())) {
				countSharedBigrams1++;
			}
		}

		// find all unique bigrams in phrase's 2nd word

		Hashtable uniqueBigramsInPhraseWord2 = new Hashtable();
		int countBigramsInPhraseWord2;
		for (i = 0; i < phraseWord2LowerCase.length() - 1; i++) {
			uniqueBigramsInPhraseWord2.put(phraseWord2LowerCase.substring(i, i+2), new Integer(1));
		}
		countBigramsInPhraseWord2 = uniqueBigramsInPhraseWord2.size();

		// count all shared bigrams

		int countSharedBigrams2 = 0;
		for (Enumeration e = uniqueBigramsInWord.keys(); e.hasMoreElements();) {
			if (uniqueBigramsInPhraseWord2.containsKey(e.nextElement())) {
				countSharedBigrams2++;
			}
		}

		// calculate dice scores

		float diceScore1;
		if ((countBigramsInWord == 0) || (countBigramsInPhraseWord1 == 0)) {
			diceScore1 = 0;
		} else {
			diceScore1 = (float)countSharedBigrams1 / countBigramsInPhraseWord1;   // ????????????? ##############
			// which is the same as
			// diceScore = (2 * (float)countSharedBigrams1) / (countBigramsInPhraseWord1 * 2);
			// where we sort of pretend the phrase is of the same length as the word
		}

		float diceScore2;
		if ((countBigramsInWord == 0) || (countBigramsInPhraseWord2 == 0)) {
			diceScore2 = 0;
		} else {
			diceScore2 = (float)countSharedBigrams2 / countBigramsInPhraseWord2;   // ????????????? ##############
			// which is the same as
			// diceScore = (2 * (float)countSharedBigrams2) / (countBigramsInPhraseWord2 * 2);
			// where we sort of pretend the phrase is of the same length as the word
		}

		// decide if scores are high enough

		return ((diceScore1 >= diceMinCountingScore) && (diceScore2 >= diceMinCountingScore));

	}

	public static boolean anchorMatch(Pattern compiledAnchorPattern, String word) {

		// is the word word an occurrence of the anchor word anchorWord?
		Matcher matcher = compiledAnchorPattern.matcher(word);

        return matcher.matches();
	}

	public static boolean badLengthCorrelation(int length1, int length2, int elementCount1, int elementCount2, float ratio) {

		// some dupl code adjustForLengthCorrelation
		float killLimit = 0.5f;   // less tolerant limit for 1-2 and 2-1, above which such alignments score lethally low
		float c = (float)(2 * Math.abs(0.0f + ratio*length1 - length2) / (ratio*length1 + length2));
		return (((elementCount1 > 0) && (elementCount2 > 0) && (elementCount1 != elementCount2)) && (c > killLimit));

	}
	// end 2006-09-20

	//public static float adjustForLengthCorrelation(float score, int length1, int length2) {
	//public static float adjustForLengthCorrelation(float score, int length1, int length2, float ratio) {
	public static float adjustForLengthCorrelation(float score, int length1, int length2, int elementCount1, int elementCount2, float ratio) {

		// two units are compared, each consisting of one (???????????????) or more elements.
		// this methods calculates how well the lengths of the two compare,
		// and adjusts the score

		// ### formelen er litt merkelig. bør forbedres

		float newScore = 0.0f;
		float lowerLimit = 0.4f;
		float upperLimit = 1.0f;
		float killLimit = 0.5f;   // less tolerant limit for 1-2 and 2-1, above which such alignments score lethally low
		//float c = (float)(2 * Math.abs(0.0f + length1 - length2) / (length1 + length2));
		float c = (float)(2 * Math.abs(0.0f + ratio*length1 - length2) / (ratio*length1 + length2));

		if ((elementCount1 > 0) && (elementCount2 > 0) && (elementCount1 != elementCount2)) {

			// 1-2 or 2-1.
			// be less tolerant of length differences

			if (c < lowerLimit/2) {
				newScore = score + 2;
			} else if (c < lowerLimit) {
				newScore = score + 1;
			} else if (c > killLimit) {
				// 'less tolerant' might be an understatement.
				// actually kill this path altogether by setting a very low score
				//newScore = -Float.MAX_VALUE;
				//newScore = -99999.0f;
				newScore = AlignmentModel.ELEMENTINFO_SCORE_HOPELESS;   // 2006-09-20
			} else {
				newScore = score;
			}

		} else {

			//System.out.println("lengthCorrelation(). length1=" + length1 + "(" + ratio*length1 + "), length2=" + length2 + ", c=" + c);
			if (c < lowerLimit/2) {
				newScore = score + 2;
			} else if (c < lowerLimit) {
				newScore = score + 1;
			} else if (c > upperLimit) {
				newScore = score / 3;
			} else {
				newScore = score;   // (2005-08-17)
			}

		}
		//System.out.println("@@@ lengthCorrelation(). modifisert score (newScore) =" + newScore);

		return newScore;

	}

}

