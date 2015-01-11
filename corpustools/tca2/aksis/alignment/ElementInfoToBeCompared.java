package aksis.alignment;

import java.util.List;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Collections;
import java.util.Locale;

import java.text.NumberFormat;
import java.text.DecimalFormat;

/**
 * some elements are to be compared,
 * either the elements in a step to be tried out,
 * or the elements under alignment, visible in the gui.
 * this class contains (refers to) the elements to be compared.
 * to be more precise the elements refered to
 * are ElementInfo objects in the Compare object.
 * methods that need to know the score of the element comparison,
 * or details about how they match,
 * must establish an ElementInfoToBeCompared object,
 * and call the object's getScore or toString method
 */
class ElementInfoToBeCompared {

	private AlignmentModel model;
	public static final String INDENT = "  ";
	List[] info = new ArrayList[Alignment.NUM_FILES];   // lists of ElementInfo, one for each text
	Clusters commonClusters;
    // score and details. calculated on demand, and only once
	private float score = AlignmentModel.ELEMENTINFO_SCORE_NOT_CALCULATED;   // set by toList(). can be got by getScore(). see getScore() §§§§§§§§§§§§§§§§§§§§ // 2006-09-20
	List<String> ret = new ArrayList<String>();   // 2006-11-20

	public ElementInfoToBeCompared(AlignmentModel model) {

		this.model = model;

		for (int t=0; t<Alignment.NUM_FILES; t++) {
			info[t] = new ArrayList<ElementInfo>();   // 2006-11-20
		}
        commonClusters = new Clusters();
	}

	public void add(ElementInfo elementInfo, int t) {

		//££££SKAL DENNE METODEN SØRGE FOR AT INFORMASJONEN OM ORD-POSISJON BLIR "GLOBAL",
		//OG IKKE LOKAL FOR HVERT ELEMENT?
		//nei, det går vel ikke, for denne klassen eier ikke elementene
		info[t].add(elementInfo);
	}

	public boolean empty() {
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			if (info[t].size() == 0) {
				return true;
			}
		}

		return false;
	}

	public float getScore() {
		if (score == AlignmentModel.ELEMENTINFO_SCORE_NOT_CALCULATED) {
            score = reallyGetScore();
		}
		
		return score;
	}

	public List toList() {

		//System.out.print("entering toList(). score=" + score + ". ");

		DecimalFormat myFormatter = (DecimalFormat)NumberFormat.getInstance(Locale.ENGLISH);
		myFormatter.applyPattern("0.###");

		//System.out.println("enter ElementInfoToBeCompared.toList() ============================");
		//System.out.println("&&& enter ElementInfoToBeCompared.toString(). score = " + score);
		//if (score <= -0.9f) {   // i.e, == -1.0f, i.e, not calculated
		if (score == AlignmentModel.ELEMENTINFO_SCORE_NOT_CALCULATED) {   // 2006-09-20. this change corrects an error. earlier element-info with calculated score -99999.0 (menat to kill path) would get their score re-calculated
			// not been calculated yet.
			//System.out.print("score not calculated yet. ");

			score = 0.0f;
			//System.out.println("&&& ElementInfoToBeCompared.toString(). init score = " + score);

			if (empty()) {

				// keep score 0. keep str ""
				//System.out.println("&&& ElementInfoToBeCompared.toString(). empty. keep score 0. keep str null string");

			} else {

				int t;
				int tt;
				Iterator it;
				Iterator it1;
				Iterator it2;
				String retLine;   // to contain one line of info

				// 2006-04-05

				// 2006-09-20
				//////////////////
				// bad lengths? //
				//////////////////

				int[] length = new int[Alignment.NUM_FILES];   // length in chars of the relevant elements of each text
				int[] elementCount = new int[Alignment.NUM_FILES];   // number of relevant elements from each text

				for (t=0; t<Alignment.NUM_FILES; t++) {
					length[t] = 0;
					it = info[t].iterator();
					while (it.hasNext()) {
						ElementInfo info1 = (ElementInfo)it.next();
						length[t] += info1.length;
					}
					elementCount[t] = info[t].size();
				}

				if (SimilarityUtils.badLengthCorrelation(length[0], length[1], elementCount[0], elementCount[1], model.getLengthRatio())) {

					score = AlignmentModel.ELEMENTINFO_SCORE_HOPELESS;
					retLine = "Very poor length match";
					ret.add(retLine);

				} else {
				// end 2006-09-20

					// this methods produces detailed information about how the
					// elements under consideration match,
					// and collects that information in List ret

					// do reporting###

					// we don't know the common score for the word based methods yet.
					// we'll have to come back and insert the score later.
					retLine = INDENT + "Word based methods score: ";
					ret.add(retLine);
					// remember in which line to insert the score later
					int wordMethodsScoreLineNumber = ret.size() - 1;

					// end 2006-04-05

					//////////////////
					// anchor words //
					//////////////////

					Clusters anchorWordClusters = new Clusters();   // 2006-04-05

					//int anchorWordScore = 0;   // 2006-04-05

					AnchorWordHit hit;
					int index;
					//int high = 0;   // 2006-04-05
					//int highSum = 0;   // 2006-04-05
					//int low = 0;   // 2006-04-05
					//int lowSum = 0;   // 2006-04-05
					//int oneSum = 0;   // 2006-04-05
					int count;
					int smallest;
					int smallestCount;
					int matchType;
					float weight;
					String word;
					int pos;
					int len;
					int elementNumber ;
					int indentLevel;
					boolean includeMatchType;

					//System.out.println("&&& ElementInfoToBeCompared.toString(). not empty. go ahead and calculate");
					// for each text t make a list hits[t] of anchor word hits
					// for (from) the elements under consideration from text t.
					// a hit is an occurrence of an anchor word in a text,
					// but not yet a confirmed match with a word from the other text ###

					//List[] hits = new ArrayList[Alignment.NUM_FILES];
					List<AnchorWordHit>[] hits = new ArrayList[Alignment.NUM_FILES];   // 2006-11-20
					for (t=0; t<Alignment.NUM_FILES; t++) {
						//hits[t] = new ArrayList();
						hits[t] = new ArrayList<AnchorWordHit>();   // 2006-11-20
						//System.out.println("før anchor words sin 'it = info[t].iterator();'");
						it = info[t].iterator();   //£££ER DETTE LØKKE OVER ELEMENTER?
						//System.out.println("etter anchor words sin 'it = info[t].iterator();'");
						///////////////@@@@@@@@@@int offset = 0;   // 2006-04-05
						while (it.hasNext()) {
							ElementInfo info1 = (ElementInfo)it.next();
							it2 = info1.anchorWordHits.hits.iterator();
							while (it2.hasNext()) {
								hit = (AnchorWordHit)it2.next();   //£££DA HAR hit HER EN NUMMERERING AV ORDPOSISJON SOM ER LOKAL FOR HVERT ELEMENT.
								//System.out.println("adder " + hit + " for tekst nr " + t);
								// change word position from local within each element
								// to global within all the elements under consideration for text t.
								// ####alternativ: operere med to-nivå nummerering i hit-ene etc:
								// 1 elementnummer, 2 lokalt ordnummer
								//System.out.println("hit.getPos() før   = " + hit.getPos());
								///////////////@@@@@@@@@@if (offset != 0) { hit.setPos(hit.getPos() + offset); }   // 2006-04-05
								//System.out.println("hit.getPos() etter = " + hit.getPos());
								hits[t].add(hit);
							}
							///////////////@@@@@@@@@@offset += info1.words.length;   // 2006-04-05
						}
						//System.out.println("hits[" + t + "] = " + hits[t]);
					}

					// see if any hits match up,
					// i.e, if any occurring anchor words in different texts
					// share the same anchor word list entry

					// sort these lists of hits on
					// (1) index (anchor word list entry number) and
					// (2) word
					for (t=0; t<Alignment.NUM_FILES; t++) {
						Collections.sort(hits[t], new AnchorWordHitComparator());
						//System.out.println("sortert hits[" + t + "] = " + hits[t]);
					}

					// match up hits.
					// first init pointers to current hit in each list
					int[] current = new int[Alignment.NUM_FILES];
					for (t=0; t<Alignment.NUM_FILES; t++) {
						current[t] = 0;
						//System.out.println("pointer to current hit in text " + t + " = " + current[t]);
					}

					// then do stuff.
					// one loop pass per anchor word list entry with hits.
					// do them in index order, smallest first
					// (we just had them sorted just for this reason)
					boolean done = false;
					while (!done) {
						//System.out.println("next pass while (!done)");
						// find smallest anchor word list index in remaining hits.
						// check if it is present inn all texts
						smallest = Integer.MAX_VALUE;
						smallestCount = 0;
						//System.out.println("smallest anchor word list index so far = " + smallest);
						for (t=0; t<Alignment.NUM_FILES; t++) {
							//System.out.println("next text - " + t);
							if (current[t] < hits[t].size()) {
								//System.out.println("there are remaining hits for text " + t);
								// there are remaining hits for text t
								hit = (AnchorWordHit)((List)hits[t]).get(current[t]);   // ### (AnchorWordHit)
								if (hit.getIndex().intValue() < smallest) {
									// found a new smallest
									smallest = hit.getIndex().intValue();
									// reset count
									smallestCount = 1;
									//System.out.println("found a smaller one: " + smallest);
								} else if (hit.getIndex().intValue() == smallest) {
									// same smallest. increment count
									smallestCount++;
								} // else not a smallest
							}
						}
						boolean presentInAllTexts = (smallestCount == Alignment.NUM_FILES);
						/*if (presentInAllTexts) {
							//System.out.println("hit for index " + smallest + " present in all texts");
						} else {
							//System.out.println("hit for index " + smallest + " not present in all texts");
						}*/
						// in the following: collect data for output only if the hit### was present in all texts
						// ...
						if (smallest == Integer.MAX_VALUE) {
							//System.out.println("found no remaining hits, for any text");
							// no remaining hits, for any text
							done = true;
						} else {
							// there are remaining hits, at least for some of the texts.
							// find all hits with this smallest remaining anchor word list index.
							//// look through all texts and find the highest/lowest number of hits in any text.
							//// this highest/lowest number might be the contribution to the anchor word score
							//// for this anchor word list entry,
							//// provided the hit is in every text..
							//// example:
							//// anchor word entry: "xxx/yyy,yy"
							//// texts: "I saw a xxx going down the xxx" vs "Jeg så en yyy nede i yy yyy"
							//// (§§§§§§§§§idiotisk, ubrukelig eksempel)
							//// 2 hits in first text and 3 hits in second text makes a score of max(2,3) = 3
							//System.out.println("there are remaining hits, at least for some of the texts");
							//high = 0;
							//low = Integer.MAX_VALUE;
							//System.out.println("highest number of hits in any text so far = " + high);
							//System.out.println("lowest number of hits in any text so far = " + low);
							//retLine = "";   // init next line of info // 2006-04-05
							for (t=0; t<Alignment.NUM_FILES; t++) {
								//System.out.println("next text - " + t);
								/*if (presentInAllTexts) {
									if (t == 0) {
										// ¤¤¤ hvorfor brukes ikke toString-metode? duplisert programmering
										//str.append(INDENT + INDENT + (smallest + 1) + " ");   // +1 since we want anchor word entries numbered from 1 and upwards when they are displayed
										retLine += INDENT + INDENT + (smallest + 1) + " ";   // +1 since we want anchor word entries numbered from 1 and upwards when they are displayed
									} else {
										//str.append("/");
										retLine += "/";
									}
								}*/ // 2006-04-05
								count = 0;
								//System.out.println("number of hits in current text so far = " + count);
								boolean first = true;
								if (current[t] < hits[t].size()) {
									//System.out.println("there are remaining hits, at least for text " + t);
									// there are remaining hits for text t.
									// get all hits with smallest index, if any
									boolean done2 = false;
									for (int c = current[t]; !done2; c++) {
										//System.out.println("check hit " + c + " for text " + t);
										hit = (AnchorWordHit)hits[t].get(c);
										//System.out.println("hit = " + hit);
										index = hit.getIndex().intValue();
										if (index == smallest) {
											//System.out.println("this is a smallest hit");
											//// samle opp ordet i en ### liste for text t, såsant det er et nytt ord
											// add to cluster list   // 2006-04-05
											elementNumber = hit.getElementNumber();   // 2006-04-05
											pos = hit.getPos();   // 2006-04-05
											//System.out.println("t = " + t + ", elementNumber = " + elementNumber + ", pos = " + pos);
											word = hit.getWord();   // 2006-04-05
											len = Utils.countWords(word);   // 2006-04-07 ### hadde vært penere med egen member len i tillegg til pos, slik som Ref har
											matchType = index;   // each anchor word entry is its own match type, sort of   // 2006-04-05
											//weight = 1.0f;   // 2006-04-05
											if (len > 1) {   // (2006-04-10)
												weight = model.getAnchorPhraseMatchWeight();   // 2006-04-07
											} else {   // (2006-04-10)
												weight = model.getAnchorWordMatchWeight();   // 2006-04-07
											}   // (2006-04-10)
											//Ref ref = new Ref(matchType, weight, t, elementNumber, pos, word);   // 2006-04-05
											//System.out.println("legger ny ref i anchorWordClusters: " + ref);
											//anchorWordClusters.add(ref);   // ### heller en addRef-metode? handler om grenseoppgang mellom clustergreiene og utsiden   // 2006-04-05
											// ### 2006-04-06 her er det et problem. vi adder én ref om gangen, og de samler seg ikke i cluster.
											// må enten adde dem i par eller hele clustre, eller må vi ha en annen addemetode for anker-ref,
											// slik at ref-ene havner i samme cluster når de har samme ankerordentry.
											// eller den addemetoden som vi har må behandle anker-ref annerledes.
											// matchemetoden, mener jeg!
											// ja - gjør det siste. lar matchemetoden behandle anker-ref annerledes.
											// forresten. får da inn ref-er som ikke har med matching å gjøre,
											// f.eks to forekomster av samme ankerord i samme tekst.
											// og uansett får jeg jo også cluster med enslig ref, når jeg gir én ref om gangen.
											// aha. disse siste problemene har jo med hva jeg gjør her.
											// addingen skal behandle anker-ref annerledes,
											// men her i denne metoden må jeg adde ref bare når presentInAllTexts
											//anchorWordClusters.add(new Ref(matchType, weight, t, elementNumber, pos, word));   // ### heller en addRef-metode? handler om grenseoppgang mellom clustergreiene og utsiden   // 2006-04-05
											// ...
											/*if (first) {
												first = false;
											} else {
												if (presentInAllTexts) {
													//str.append(",");
													retLine += ",";
												}
											}*/
											if (presentInAllTexts) {
												//str.append(hit.getWord());
												//retLine += hit.getWord();
												//anchorWordClusters.add(new Ref(matchType, weight, t, elementNumber, pos, word));   // ### heller en addRef-metode? handler om grenseoppgang mellom clustergreiene og utsiden   // 2006-04-06
												anchorWordClusters.add(new Ref(matchType, weight, t, elementNumber, pos, len, word));   // ### heller en addRef-metode? handler om grenseoppgang mellom clustergreiene og utsiden   // 2006-04-07
											}
											count++;
											//System.out.println("number of hits in current text so far = " + count);
										} else {
											done2 = true;
										}
										if (c+1 >= hits[t].size()) {
											done2 = true;
										}
									}
									// ...
									current[t] += count;
									//System.out.println("updated pointer to current hit in text " + t + " to " + current[t]);
								}
								//if (count > high) { high = count; }
								//if (count < low) { low = count; }
							}
						}
					}
					float anchorWordScore = anchorWordClusters.getScore(model.getLargeClusterScorePercentage());

					retLine = INDENT + INDENT + "Anchor word score: " + myFormatter.format(anchorWordScore);   // 2006-04-05
					ret.add(retLine);   // 2006-04-05

					indentLevel = 3;   // 2006-04-05
					includeMatchType = true;   // i.e, include anchor word entry number. ### + 1 ### ugly
					ret.addAll(anchorWordClusters.getDetails(indentLevel, includeMatchType));   // getDetails() does its own indentation and endline. ### ikke helt bra?   // 2006-04-05

					// check all the words in one text against all the words in the other.
					// collect clusters of proper names.
					// collect clusters of dice-related words.
					// collect clusters of numbers.
					// (usually all the words in a cluster will be related to each other,
					// but not necessarily.)
					String word1;
					String word2;
					String nextWord1;   // 2006-04-07
					String nextWord2;   // 2006-04-07
					//String phrase1;   // 2006-04-07. words glued together without space between them
					//String phrase2;   // 2006-04-07. words glued together without space between them
					String showPhrase1;   // 2006-04-18. words with space between them
					String showPhrase2;   // 2006-04-18. words with space between them
					//Clusters properNameClusters = new Clusters(model.getClusterScoreMethod());
					Clusters properNameClusters = new Clusters();   // 2006-04-05
					//Clusters diceClusters = new Clusters(model.getClusterScoreMethod());
					Clusters diceClusters = new Clusters();   // 2006-04-05
					Clusters numberClusters = new Clusters();   // 2006-04-06
					//System.out.println("Skipper proper, dice, numbers");
					for (t=0; t<Alignment.NUM_FILES; t++) {
						for (tt=t+1; tt<Alignment.NUM_FILES; tt++) {
							//System.out.println("\nneste (eneste) gjennomløp. t = " + t + ". tt = " + tt);

							// check text t against text tt
							// (in practice text 0 (known to the user as text 1)
							// against text 1 (known to the user as text 2))

							// ... each word in relevant elements of text t

							it1 = info[t].iterator();
							while (it1.hasNext()) {
								ElementInfo info1 = (ElementInfo)it1.next();
								for (int x = 0; x < info1.words.length; x++) {

									word1 = info1.words[x];
									// 2006-04-07
									if (x < info1.words.length - 1) {
										nextWord1 = info1.words[x+1];
									} else {
										nextWord1 = "";
									}

									// end 2006-04-07
									// ... each word in relevant elements of text tt

									it2 = info[tt].iterator();
									while (it2.hasNext()) {
										ElementInfo info2 = (ElementInfo)it2.next();
										for (int y = 0; y < info2.words.length; y++) {

											word2 = info2.words[y];
											// 2006-04-07
											if (y < info2.words.length - 1) {
												nextWord2 = info2.words[y+1];
											} else {
												nextWord2 = "";
											}
											// end 2006-04-07

											// compare two words

											// proper names

											if (Character.isUpperCase(word1.charAt(0)) && Character.isUpperCase(word2.charAt(0)) && word1.equals(word2)) {

												// the words are capitalized and equal.
												// add to cluster list

												//System.out.println("\n" + word1 + " and " + word2 + " are capitalized and equal. add to cluster list");
												//properNameClusters.add(t, tt, x, y);
												//properNameClusters.add(t, tt, x, y, word1, word2);
												matchType = Match.PROPER;   // 2006-04-05
												//weight = 1.0f;   // 2006-04-05
												weight = model.getProperNameMatchWeight();   // 2006-04-07
												//properNameClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, word1, word2);   // 2006-04-05
												properNameClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, 1, 1, word1, word2);   // 2006-04-07
												//System.out.println("%%% properNameClusters etter add = " + properNameClusters);

											}

											// dice

											// first check if the words are long enough to be considered
											if ((word1.length() >= model.getDiceMinWordLength()) && (word2.length() >= model.getDiceMinWordLength())) {

												//System.out.println("\nskal dice-sammenlikne " + word1 + " med " + word2);
												//if (SimilarityUtils.dice(word1, word2) >= model.getDiceMinCountingScore()) {
												if (SimilarityUtils.diceMatch(word1, word2, model.getDiceMinCountingScore())) {   // 2006-08-09

													// the words are related.
													// add to cluster list

													//System.out.println("\n" + word1 + " and " + word2 + " are dice-related. add to cluster list");
													//diceClusters.add(t, tt, x, y, word1, word2);
													matchType = Match.DICE;   // 2006-04-05
													//weight = 1.0f;   // 2006-04-05
													weight = model.getDiceMatchWeight();   // 2006-04-07
													//diceClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, word1, word2);   // 2006-04-05
													diceClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, 1, 1, word1, word2);   // 2006-04-07

												}

											}

											// 2006-04-07

											// also try dice on 2 words against 1 word...

											if (nextWord1 != "") {

												//phrase1 = word1 + " " + nextWord1;
												//phrase1 = word1 + nextWord1;
												showPhrase1 = word1 + " " + nextWord1;   // 2006-04-18

												// first check if the phrases/words are long enough to be considered
												//if ((phrase1.length()-1 >= model.getDiceMinWordLength()) && (word2.length() >= model.getDiceMinWordLength())) {
												//if ((phrase1.length() >= model.getDiceMinWordLength()) && (word2.length() >= model.getDiceMinWordLength())) {
												if (   (word1.length()     >= model.getDiceMinWordLength())
												    && (nextWord1.length() >= model.getDiceMinWordLength())
												    && (word2.length()     >= model.getDiceMinWordLength())) {   // 2006-04-18

													//if (SimilarityUtils.dice(phrase1, word2) >= model.getDiceMinCountingScore()) {
													//if (SimilarityUtils.dice(phrase1, word2, "2-1") >= model.getDiceMinCountingScore()) {   // 2006-04-18
													if (SimilarityUtils.diceMatch(word1, nextWord1, word2, "2-1", model.getDiceMinCountingScore())) {   // 2006-08-09

														// the phrases/words are related.
														// add to cluster list

														//System.out.println("\n" + phrase1 + " and " + word2 + " are dice-related. add to cluster list");
														matchType = Match.DICE;   // 2006-04-05
														weight = model.getDicePhraseMatchWeight();   // 2006-04-07
														//diceClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, 2, 1, phrase1, word2);
														diceClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, 2, 1, showPhrase1, word2);   // 2006-04-18

													}

												}

											}

											// ...and 1 word against 2 words

											if (nextWord2 != "") {

												//phrase2 = word2 + " " + nextWord2;
												//phrase2 = word2 + nextWord2;
												showPhrase2 = word2 + " " + nextWord2;   // 2006-04-18

												// first check if the phrases/words are long enough to be considered
												//if ((word1.length() >= model.getDiceMinWordLength()) && (phrase2.length()-1 >= model.getDiceMinWordLength())) {
												//if ((word1.length() >= model.getDiceMinWordLength()) && (phrase2.length() >= model.getDiceMinWordLength())) {
												if (   (word1.length()     >= model.getDiceMinWordLength())
												    && (word2.length()     >= model.getDiceMinWordLength())
												    && (nextWord2.length() >= model.getDiceMinWordLength())) {   // 2006-04-18

													//if (SimilarityUtils.dice(word1, phrase2) >= model.getDiceMinCountingScore()) {
													//if (SimilarityUtils.dice(word1, phrase2, "1-2") >= model.getDiceMinCountingScore()) {   // 2006-04-18
													if (SimilarityUtils.diceMatch(word1, word2, nextWord2, "1-2", model.getDiceMinCountingScore())) {   // 2006-08-09

														// the phrases/words are related.
														// add to cluster list

														//System.out.println("\n" + word1 + " and " + phrase2 + " are dice-related. add to cluster list");
														matchType = Match.DICE;   // 2006-04-05
														weight = model.getDicePhraseMatchWeight();   // 2006-04-07
														//diceClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, 1, 2, word1, phrase2);
														diceClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, 1, 2, word1, showPhrase2);   // 2006-04-18

													}

												}

											}

											// end 2006-04-07

											// 2006-04-06

											// numbers

											float num1;
											float num2;
											try {
												num1 = Float.parseFloat(word1);
												num2 = Float.parseFloat(word2);
												if (num1 == num2) {

													// same number
													// add to cluster list

													matchType = Match.NUMBER;
													//weight = 1.0f;
													weight = model.getNumberMatchWeight();   // 2006-04-07
													//numberClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, word1, word2);
													numberClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, 1, 1, word1, word2);   // 2006-04-07

												}

											} catch (NumberFormatException ne) {
											}

											// end 2006-04-06

										}
									}

								}

							}
						}
					}

					//System.out.println("%%% properNameClusters ferdig = " + properNameClusters);

					//int properNameScore = properNameClusters.getScore(model.getClusterScoreMethod());
					//float properNameScore = properNameClusters.getScore(model.getClusterScoreMethod());
					float properNameScore = properNameClusters.getScore(model.getLargeClusterScorePercentage());

					//int diceScore = diceClusters.getScore(model.getClusterScoreMethod());
					//float diceScore = diceClusters.getScore(model.getClusterScoreMethod());
					float diceScore = diceClusters.getScore(model.getLargeClusterScorePercentage());

					//int numberScore = numberClusters.getScore(model.getClusterScoreMethod());
					//float numberScore = numberClusters.getScore(model.getClusterScoreMethod());
					float numberScore = numberClusters.getScore(model.getLargeClusterScorePercentage());

					// ...

					//str.append(INDENT + "Proper name score: " + properNameScore + "\n");
					retLine = INDENT + INDENT + "Proper name score: " + myFormatter.format(properNameScore);   // 2006-04-05
					ret.add(retLine);

					//score += properNameScore;   // 2006-04-05

					//str.append(properNameClusters.getWords());   // getWords() does its own indentation and endline. ### ikke helt bra?
					//ret.addAll(properNameClusters.getDetails());   // getDetails() does its own indentation and endline. ### ikke helt bra?
					indentLevel = 3;   // 2006-04-05
					includeMatchType = false;
					ret.addAll(properNameClusters.getDetails(indentLevel, includeMatchType));   // getDetails() does its own indentation and endline. ### ikke helt bra?   // 2006-04-05

					//str.append(INDENT + "Dice score: " + diceScore + "\n");
					retLine = INDENT + INDENT + "Dice score: " + myFormatter.format(diceScore);   // 2006-04-05
					ret.add(retLine);

					//score += diceScore;   // 2006-04-05

					//str.append(diceClusters.getWords());   // getWords() does its own indentation and endline. ### ikke helt bra?
					//ret.addAll(diceClusters.getDetails());   // getDetails() does its own indentation and endline. ### ikke helt bra?
					indentLevel = 3;   // 2006-04-05
					includeMatchType = false;
					ret.addAll(diceClusters.getDetails(indentLevel, includeMatchType));   // getDetails() does its own indentation and endline. ### ikke helt bra?   // 2006-04-05

					// 2006-04-06

					retLine = INDENT + INDENT + "Number score: " + myFormatter.format(numberScore);
					ret.add(retLine);

					indentLevel = 3;
					includeMatchType = false;
					ret.addAll(numberClusters.getDetails(indentLevel, includeMatchType));

					// end 2006-04-06

					// 2006-04-05

					////////////////////////////////

					// common score for anchor words, proper names, dice and numbers

					commonClusters.add(anchorWordClusters);
					commonClusters.add(properNameClusters);
					commonClusters.add(diceClusters);
					commonClusters.add(numberClusters);   // 2006-04-06

					//int commonScore = commonClusters.getScore(model.getClusterScoreMethod());
					//float commonScore = commonClusters.getScore(model.getClusterScoreMethod());
					float commonScore = commonClusters.getScore(model.getLargeClusterScorePercentage());

					// go back and insert the common score for the word based methods
					ret.set(wordMethodsScoreLineNumber, (String)ret.get(wordMethodsScoreLineNumber) + myFormatter.format(commonScore));

					score += commonScore;

					// end 2006-04-05

					// debugging or testing
// 					String tempo = commonClusters.nonTrivialClusters_ToString();
// 					if (tempo != "") {
// 						System.out.println(tempo);
// 					}

					////////////////////////////////
					// scoring special characters //
					////////////////////////////////

					//int scoringCharacterScore = 0;   // 2006-04-05

					// check all the ... ... ...

					String char1;
					String char2;
					//Clusters scoringCharacterClusters = new Clusters(model.getClusterScoreMethod());
					Clusters scoringCharacterClusters = new Clusters();   // 2006-04-05
					for (t=0; t<Alignment.NUM_FILES; t++) {
						for (tt=t+1; tt<Alignment.NUM_FILES; tt++) {

							// check text t against text tt (in practice 0 (1) against 1 (2))

							// each scoring special character in relevant elements of text t

							it1 = info[t].iterator();
							while (it1.hasNext()) {
								ElementInfo info1 = (ElementInfo)it1.next();
								//System.out.println("info1.scoringCharacters = " + info1.scoringCharacters);
								for (int x = 0; x < info1.scoringCharacters.length(); x++) {
									char1 = info1.scoringCharacters.substring(x, x+1);

									// ... each scoring char in relevant elements of text tt

									it2 = info[tt].iterator();
									while (it2.hasNext()) {
										ElementInfo info2 = (ElementInfo)it2.next();
										//System.out.println("info2.scoringCharacters = " + info2.scoringCharacters);
										for (int y = 0; y < info2.scoringCharacters.length(); y++) {
											char2 = info2.scoringCharacters.substring(y, y+1);

											// compare two characters

											if (char1.equals(char2)) {

												// equal.
												// add to cluster list

												//scoringCharacterClusters.add(t, tt, x, y, char1, char2);
												matchType = Match.SCORING_CHARACTERS;   // ### irrelevant   // 2006-04-05
												//weight = 1.0f;   // 2006-04-05
												weight = model.getScoringCharacterMatchWeight();   // 2006-04-07
												//scoringCharacterClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, char1, char2);   // 2006-04-05
												scoringCharacterClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, 1, 1, char1, char2);   // 2006-04-07

											}

										}
									}

								}

							}

						}
					}

					//int scoringCharacterScore = scoringCharacterClusters.getScore(model.getClusterScoreMethod());
					//float scoringCharacterScore = scoringCharacterClusters.getScore(model.getClusterScoreMethod());
					float scoringCharacterScore = scoringCharacterClusters.getScore(model.getLargeClusterScorePercentage());

					// ...

					//str.append(INDENT + "Scoring special characters score: " + scoringCharacterScore + "\n");
					//retLine = INDENT + "Scoring special characters score: " + scoringCharacterScore;
					retLine = INDENT + "Special characters score: " + myFormatter.format(scoringCharacterScore);
					ret.add(retLine);

					score += scoringCharacterScore;

					//str.append(scoringCharacterClusters.getWords());   // getWords() does its own indentation and endline. ### ikke helt bra?
					//ret.addAll(scoringCharacterClusters.getDetails());   // getDetails() does its own indentation and endline. ### ikke helt bra?
					indentLevel = 2;   // 2006-04-05
					includeMatchType = false;
					ret.addAll(scoringCharacterClusters.getDetails(indentLevel, includeMatchType));   // getDetails() does its own indentation and endline. ### ikke helt bra?   // 2006-04-05

					////////////
					// length //
					////////////

					/* 2006-09-20
					int[] length = new int[Alignment.NUM_FILES];   // length in chars of the relevant elements of each text
					int[] elementCount = new int[Alignment.NUM_FILES];   // number of relevant elements from each text

					for (t=0; t<Alignment.NUM_FILES; t++) {
						length[t] = 0;
						it = info[t].iterator();
						while (it.hasNext()) {
							ElementInfo info1 = (ElementInfo)it.next();
							length[t] += info1.length;
						}
						elementCount[t] = info[t].size();
					}
					*/

					// ...
					float scoreBefore = score;
					//score = SimilarityUtils.adjustForLengthCorrelation(score, length[0], length[1]);
					//score = SimilarityUtils.adjustForLengthCorrelation(score, length[0], length[1], model.getLengthRatio());
					score = SimilarityUtils.adjustForLengthCorrelation(score, length[0], length[1], elementCount[0], elementCount[1], model.getLengthRatio());
					//System.out.println(">>> score = " + score + "\n");

					retLine = "Lengths " + length[0] + " (" + myFormatter.format(length[0]*model.getLengthRatio()) + ") and " + length[1];
					if (score > scoreBefore) {
						//str.append("Lengths " + length[0] + " and " + length[1] + " match well,\n" + INDENT + "increasing score from " + scoreBefore + " to " + score + "\n");
						//retLine = "Lengths " + length[0] + " and " + length[1] + " match well,";
						retLine += " match well,";
						ret.add(retLine);
						retLine = INDENT + "increasing score from " + myFormatter.format(scoreBefore) + " to " + myFormatter.format(score);
						ret.add(retLine);
					} else if (score < scoreBefore) {
						//str.append("Lengths " + length[0] + " and " + length[1] + " don't match well,\n" + INDENT + "reducing score from " + scoreBefore + " to " + score + "\n");
						//retLine = "Lengths " + length[0] + " and " + length[1] + " don't match well,";
						retLine += " don't match well,";
						ret.add(retLine);
						retLine = INDENT + "reducing score from " + myFormatter.format(scoreBefore) + " to " + myFormatter.format(score);
						ret.add(retLine);
					} else {
						//str.append("Lengths " + length[0] + " and " + length[1] + " match so-so,\n" + INDENT + "making no change to the score " + score + "\n");
						//retLine = "Lengths " + length[0] + " and " + length[1] + " match so-so,";
						retLine += " match so-so,";
						ret.add(retLine);
						retLine = INDENT + "making no change to the score " + myFormatter.format(score);
						ret.add(retLine);
					}

					////////////////////////////////////
					// micro adjustment to break ties // 2005-11-03
					////////////////////////////////////

					// when otherwise scoring equal,
					// paths with 1-1's are to preferred
					// over paths with other alignments.
					// add (subtract) micro punishment if step is not 1-1
					boolean is11 = true;
					for (t=0; t<Alignment.NUM_FILES; t++) {
						if (info[t].size() != 1) {
							is11 = false;
						}
					}
					if (!is11) {
						score -= .001;
					}

					////////////////////////////////////

					//str.insert(0, "Total match score: " + score + "\n");
					retLine = "Total match score: " + myFormatter.format(score);
					// main header. insert at top
					ret.add(0, retLine);

				}   // 2006-09-20

			}
			//System.out.println("&&& soon leave ElementInfoToBeCompared.toString(). score = " + score);

		} else {
			//System.out.print("score already calculated. ");
		}

		//System.out.println("leaving toList(). score = " + score);

		//// return textual version §§§
		//return new String(str);
		// return textual version as a List
		//System.out.println("exit ElementInfoToBeCompared.toList() ============================");
		return ret;

	}

    float reallyGetScore() {
        if (score == AlignmentModel.ELEMENTINFO_SCORE_NOT_CALCULATED) {
            score = 0.0f;
            if (!empty()) {

                //////////////////
                // bad lengths? //
                //////////////////

                int[] length = new int[Alignment.NUM_FILES];   // length in chars of the relevant elements of each text
                int[] elementCount = new int[Alignment.NUM_FILES];   // number of relevant elements from each text

                for (int t=0; t<Alignment.NUM_FILES; t++) {
                    length[t] = 0;
                    Iterator<ElementInfo> it = info[t].iterator();
                    while (it.hasNext()) {
                        ElementInfo info1 = it.next();
                        length[t] += info1.length;
                    }
                    elementCount[t] = info[t].size();
                }

                if (SimilarityUtils.badLengthCorrelation(length[0], length[1], elementCount[0], elementCount[1], model.getLengthRatio())) {

                    score = AlignmentModel.ELEMENTINFO_SCORE_HOPELESS;

                } else {
                    score = reallyGetScore2();
                }
            }
        }
        
        return score;
    }
    
    float reallyGetScore2() {
        //////////////////
        // anchor words //
        //////////////////

           // 2006-04-05


        findAnchorWordMatches();
        // check all the words in one text against all the words in the other.
        
        
        
        // (usually all the words in a cluster will be related to each other,
        // but not necessarily.)
        for (int t=0; t<Alignment.NUM_FILES; t++) {
            for (int tt=t+1; tt<Alignment.NUM_FILES; tt++) {
                // check text t against text tt
                // (in practice text 0 (known to the user as text 1)
                // against text 1 (known to the user as text 2))
                // ... each word in relevant elements of text t
                
                // collect clusters of numbers.
                findNumberMatches(t, tt);
                // collect clusters of proper names.
                findPropernameMatches(t, tt);
                // collect clusters of dice-related words.
                findDiceMatches(t, tt);
                // collect clusters of special characters
                findSpecialCharacterMatches(t, tt);
            }
        }

        // common score for anchor words, proper names, dice, numbers and special characters
        score += commonClusters.getScore(model.getLargeClusterScorePercentage());

        ////////////
        // length //
        ////////////

        int[] length = new int[Alignment.NUM_FILES];   // length in chars of the relevant elements of each text
        int[] elementCount = new int[Alignment.NUM_FILES];   // number of relevant elements from each text

        for (int t=0; t<Alignment.NUM_FILES; t++) {
            length[t] = 0;
            Iterator<ElementInfo> it = info[t].iterator();
            while (it.hasNext()) {
                ElementInfo info1 = it.next();
                length[t] += info1.length;
            }
            elementCount[t] = info[t].size();
        }

        score = SimilarityUtils.adjustForLengthCorrelation(score, length[0], length[1], elementCount[0], elementCount[1], model.getLengthRatio());

        ////////////////////////////////////
        // micro adjustment to break ties // 2005-11-03
        ////////////////////////////////////

        // when otherwise scoring equal,
        // paths with 1-1's are to preferred
        // over paths with other alignments.
        // add (subtract) micro punishment if step is not 1-1
        boolean is11 = true;
        for (int t=0; t<Alignment.NUM_FILES; t++) {
            if (info[t].size() != 1) {
                is11 = false;
            }
        }

        if (!is11) {
            score -= .001;
        }
    
        return score;
    }
    
    void findDiceMatches(int t, int tt) {
        Iterator<ElementInfo> it1 = info[t].iterator();
        while (it1.hasNext()) {
            ElementInfo info1 = it1.next();
            for (int x = 0; x < info1.words.length; x++) {
                String word1 = info1.words[x];
                String nextWord1;
                if (x < info1.words.length - 1) {
                    nextWord1 = info1.words[x+1];
                } else {
                    nextWord1 = "";
                }

                // ... each word in relevant elements of text tt

                Iterator<ElementInfo> it2 = info[tt].iterator();
                while (it2.hasNext()) {
                    ElementInfo info2 = it2.next();
                    for (int y = 0; y < info2.words.length; y++) {
                        int matchType = Match.DICE;   // 2006-04-05
                        float weight = model.getDicePhraseMatchWeight();   // 2006-04-07
                        String word2 = info2.words[y];
                        
                        // first check if the words are long enough to be considered
                        if ((word1.length() >= model.getDiceMinWordLength()) && (word2.length() >= model.getDiceMinWordLength())) {

                            if (SimilarityUtils.diceMatch(word1, word2, model.getDiceMinCountingScore())) {   // 2006-08-09

                                // the words are related.
                                // add to cluster list
                                commonClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, 1, 1, word1, word2);   // 2006-04-07
                            }
                        }

                        // also try dice on 2 words against 1 word...

                        if (nextWord1 != "") {

                            String showPhrase1 = word1 + " " + nextWord1;   // words with space between them

                            // first check if the phrases/words are long enough to be considered
                            if (   (word1.length()     >= model.getDiceMinWordLength())
                                && (nextWord1.length() >= model.getDiceMinWordLength())
                                && (word2.length()     >= model.getDiceMinWordLength())) {   // 2006-04-18

                                if (SimilarityUtils.diceMatch(word1, nextWord1, word2, "2-1", model.getDiceMinCountingScore())) {   // 2006-08-09

                                    // the phrases/words are related.
                                    // add to cluster list
                                    commonClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, 2, 1, showPhrase1, word2);   // 2006-04-18
                                }
                            }
                        }
                        
                        // ...and 1 word against 2 words
                        String nextWord2;
                        if (y < info2.words.length - 1) {
                            nextWord2 = info2.words[y+1];
                        } else {
                            nextWord2 = "";
                        }

                        if (nextWord2 != "") {
                            String showPhrase2 = word2 + " " + nextWord2;   // words with space between them

                            // first check if the phrases/words are long enough to be considered
                            if (   (word1.length()     >= model.getDiceMinWordLength())
                                && (word2.length()     >= model.getDiceMinWordLength())
                                && (nextWord2.length() >= model.getDiceMinWordLength())) {   // 2006-04-18

                                if (SimilarityUtils.diceMatch(word1, word2, nextWord2, "1-2", model.getDiceMinCountingScore())) {   // 2006-08-09

                                    // the phrases/words are related.
                                    // add to cluster list
                                    commonClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, 1, 2, word1, showPhrase2);   // 2006-04-18
                                }
                            }
                        }

                        
                    }
                }

            }
        }
    }
    
    void findAnchorWordMatches() {

        List<AnchorWordHit>[] hits = findHits();
        // see if any hits match up,
        // i.e, if any occurring anchor words in different texts
        // share the same anchor word list entry

        // sort these lists of hits on
        // (1) index (anchor word list entry number) and
        // (2) word
        for (int t=0; t<Alignment.NUM_FILES; t++) {
            Collections.sort(hits[t], new AnchorWordHitComparator());
        }

        // match up hits.
        // first init pointers to current hit in each list
        int[] current = new int[Alignment.NUM_FILES];
        for (int t=0; t<Alignment.NUM_FILES; t++) {
            current[t] = 0;
        }

        // then do stuff.
        // one loop pass per anchor word list entry with hits.
        // do them in index order, smallest first
        // (we just had them sorted just for this reason)
        int smallest;
        int smallestCount;
        boolean done = false;
        while (!done) {
            // find smallest anchor word list index in remaining hits.
            // check if it is present inn all texts
            smallest = Integer.MAX_VALUE;
            smallestCount = 0;

            for (int t=0; t<Alignment.NUM_FILES; t++) {
                if (current[t] < hits[t].size()) {
                    // there are remaining hits for text t
                    AnchorWordHit hit = hits[t].get(current[t]);   // ### (AnchorWordHit)
                    if (hit.getIndex().intValue() < smallest) {
                        // found a new smallest
                        smallest = hit.getIndex().intValue();
                        // reset count
                        smallestCount = 1;
                    } else if (hit.getIndex().intValue() == smallest) {
                        // same smallest. increment count
                        smallestCount++;
                    } // else not a smallest
                }
            }
            boolean presentInAllTexts = (smallestCount == Alignment.NUM_FILES);

            if (smallest == Integer.MAX_VALUE) {
                // no remaining hits, for any text
                done = true;
            } else {
                hits = findMoreHits(hits, current, smallest, presentInAllTexts);
            }
        }
    }
    
    void findPropernameMatches(int t, int tt) {
        // numbers

        Iterator<ElementInfo> it1 = info[t].iterator();
        while (it1.hasNext()) {
            ElementInfo info1 = it1.next();
            for (int x = 0; x < info1.words.length; x++) {

                String word1 = info1.words[x];
                Iterator<ElementInfo> it2 = info[tt].iterator();
                while (it2.hasNext()) {
                    ElementInfo info2 = it2.next();
                    for (int y = 0; y < info2.words.length; y++) {

                        String word2 = info2.words[y];
                                // proper names

                        if (Character.isUpperCase(word1.charAt(0)) && Character.isUpperCase(word2.charAt(0)) && word1.equals(word2)) {

                            // the words are capitalized and equal.
                            // add to cluster list

                            int matchType = Match.PROPER;   // 2006-04-05
                            float weight = model.getProperNameMatchWeight();   // 2006-04-07
                            commonClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, 1, 1, word1, word2);   // 2006-04-07
                        }
                    }
                }
            }
        }
    }
    
    void findNumberMatches(int t, int tt) {
        // numbers

        Iterator<ElementInfo> it1 = info[t].iterator();
        while (it1.hasNext()) {
            ElementInfo info1 = it1.next();
            for (int x = 0; x < info1.words.length; x++) {

                String word1 = info1.words[x];
                Iterator<ElementInfo> it2 = info[tt].iterator();
                while (it2.hasNext()) {
                    ElementInfo info2 = it2.next();
                    for (int y = 0; y < info2.words.length; y++) {
                        String word2 = info2.words[y];
                        try {
                            float num1 = Float.parseFloat(word1);
                            float num2 = Float.parseFloat(word2);
                            if (num1 == num2) {

                                // same number
                                // add to cluster list

                                int matchType = Match.NUMBER;
                                float weight = model.getNumberMatchWeight();   // 2006-04-07
                                commonClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, 1, 1, word1, word2);   // 2006-04-07
                            }
                        } catch (NumberFormatException ne) {
                        }
                    }
                }
            }
        }
    }
    
    ////////////////////////////////
    // scoring special characters //
    ////////////////////////////////
    void findSpecialCharacterMatches(int t, int tt) {
        // check text t against text tt (in practice 0 (1) against 1 (2))
        // each scoring special character in relevant elements of text t
        Iterator<ElementInfo> it1 = info[t].iterator();
        while (it1.hasNext()) {
            ElementInfo info1 = it1.next();
            for (int x = 0; x < info1.scoringCharacters.length(); x++) {
                String char1 = info1.scoringCharacters.substring(x, x+1);

                // ... each scoring char in relevant elements of text tt
                Iterator<ElementInfo> it2 = info[tt].iterator();
                while (it2.hasNext()) {
                    ElementInfo info2 = it2.next();
                    for (int y = 0; y < info2.scoringCharacters.length(); y++) {
                        String char2 = info2.scoringCharacters.substring(y, y+1);

                        // compare two characters
                        if (char1.equals(char2)) {

                            // equal.
                            // add to cluster list

                            int matchType = Match.SCORING_CHARACTERS;   // ### irrelevant   // 2006-04-05
                            float weight = model.getScoringCharacterMatchWeight();   // 2006-04-07
                            commonClusters.add(matchType, weight, t, tt, info1.elementNumber, info2.elementNumber, x, y, 1, 1, char1, char2);   // 2006-04-07
                        }
                    }
                }
            }
        }
    }
    
    List<AnchorWordHit>[] findMoreHits(List<AnchorWordHit>[] hits, int[] current, int smallest, boolean presentInAllTexts) {
        Clusters anchorWordClusters = new Clusters();
        // there are remaining hits, at least for some of the texts.
        // find all hits with this smallest remaining anchor word list index.
        //// look through all texts and find the highest/lowest number of hits in any text.
        //// this highest/lowest number might be the contribution to the anchor word score
        //// for this anchor word list entry,
        //// provided the hit is in every text..
        //// example:
        //// anchor word entry: "xxx/yyy,yy"
        //// texts: "I saw a xxx going down the xxx" vs "Jeg så en yyy nede i yy yyy"
        //// (§§§§§§§§§idiotisk, ubrukelig eksempel)
        //// 2 hits in first text and 3 hits in second text makes a score of max(2,3) = 3
        for (int t=0; t<Alignment.NUM_FILES; t++) {
            int count = 0;
            boolean first = true;
            if (current[t] < hits[t].size()) {
                // there are remaining hits for text t.
                // get all hits with smallest index, if any
                boolean done2 = false;
                for (int c = current[t]; !done2; c++) {
                    AnchorWordHit hit = hits[t].get(c);
                    int index = hit.getIndex().intValue();
                    if (index == smallest) {
                        // add to cluster list   // 2006-04-05
                        int elementNumber = hit.getElementNumber();   // 2006-04-05
                        int pos = hit.getPos();   // 2006-04-05
                        String word = hit.getWord();   // 2006-04-05
                        int len = Utils.countWords(word);   // 2006-04-07 ### hadde vært penere med egen member len i tillegg til pos, slik som Ref har
                        int matchType = index;   // each anchor word entry is its own match type, sort of   // 2006-04-05
                        float weight;
                        if (len > 1) {   // (2006-04-10)
                            weight = model.getAnchorPhraseMatchWeight();   // 2006-04-07
                        } else {   // (2006-04-10)
                            weight = model.getAnchorWordMatchWeight();   // 2006-04-07
                        }   // (2006-04-10)
                        //anchorWordClusters.add(ref);   // ### heller en addRef-metode? handler om grenseoppgang mellom clustergreiene og utsiden   // 2006-04-05
                        // ### 2006-04-06 her er det et problem. vi adder én ref om gangen, og de samler seg ikke i cluster.
                        // må enten adde dem i par eller hele clustre, eller må vi ha en annen addemetode for anker-ref,
                        // slik at ref-ene havner i samme cluster når de har samme ankerordentry.
                        // eller den addemetoden som vi har må behandle anker-ref annerledes.
                        // matchemetoden, mener jeg!
                        // ja - gjør det siste. lar matchemetoden behandle anker-ref annerledes.
                        // forresten. får da inn ref-er som ikke har med matching å gjøre,
                        // f.eks to forekomster av samme ankerord i samme tekst.
                        // og uansett får jeg jo også cluster med enslig ref, når jeg gir én ref om gangen.
                        // aha. disse siste problemene har jo med hva jeg gjør her.
                        // addingen skal behandle anker-ref annerledes,
                        // men her i denne metoden må jeg adde ref bare når presentInAllTexts
                        if (presentInAllTexts) {
                            anchorWordClusters.add(new Ref(matchType, weight, t, elementNumber, pos, len, word));   // ### heller en addRef-metode? handler om grenseoppgang mellom clustergreiene og utsiden   // 2006-04-07
                        }
                        count++;
                    } else {
                        done2 = true;
                    }
                    if (c+1 >= hits[t].size()) {
                        done2 = true;
                    }
                }
                current[t] += count;
            }
        }
        
        commonClusters.add(anchorWordClusters);
        return hits;
    }
    
    List<AnchorWordHit>[] findHits() {
        // for each text t make a list hits[t] of anchor word hits
        // for (from) the elements under consideration from text t.
        // a hit is an occurrence of an anchor word in a text,
        // but not yet a confirmed match with a word from the other text ###

        List<AnchorWordHit>[] hits = new ArrayList[Alignment.NUM_FILES];   // 2006-11-20
        for (int t=0; t<Alignment.NUM_FILES; t++) {
            hits[t] = new ArrayList<AnchorWordHit>();   // 2006-11-20
            Iterator<ElementInfo> it = info[t].iterator();   //£££ER DETTE LØKKE OVER ELEMENTER?
            while (it.hasNext()) {
                ElementInfo info1 = it.next();
                Iterator<AnchorWordHit> it2 = info1.anchorWordHits.hits.iterator();
                while (it2.hasNext()) {
                    AnchorWordHit hit = it2.next();   //£££DA HAR hit HER EN NUMMERERING AV ORDPOSISJON SOM ER LOKAL FOR HVERT ELEMENT.
                    // change word position from local within each element
                    // to global within all the elements under consideration for text t.
                    // ####alternativ: operere med to-nivå nummerering i hit-ene etc:
                    // 1 elementnummer, 2 lokalt ordnummer
                    hits[t].add(hit);
                }
            }
        }

        return hits;
    }
}

