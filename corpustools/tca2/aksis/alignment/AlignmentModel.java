/*
 * AlignmentModel.java
 *
 * ...
 * ...
 * @author Oystein Reigem
 */

package aksis.alignment;

import java.awt.Toolkit;

import javax.swing.DefaultListModel;
import javax.swing.JOptionPane;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import java.util.HashMap;
import java.util.Iterator;
import java.util.TreeSet;
import java.util.Enumeration;

import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.OutputStreamWriter;

import java.nio.charset.Charset;

import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.w3c.dom.Element;
import org.w3c.dom.Document;

//////////////////////////////////////////////////////////////////////////////////////////
// apparatus for structure and flow of alignable elements through the alignment process //
//////////////////////////////////////////////////////////////////////////////////////////




/**
 *
 */
class AlignmentModel {

	// when trying to align elements
	// the program will work forward in the text trying out many possible paths
	// before selecting the best one.
	// then it will suggest or select the first step from the best path.
	// the program will try paths of length maxPathLength.
	// Why the 'Max' in the variable name?
	// Well - maxPathLength is max in two senses:
	// - paths will unavoidably be shorter at the very end of the text
	// - paths are built step by step, so intermediate paths are shorter.
	// maxPathLength is settable by the user in the settings dialog.
	// it can be set as low as 1, but not higher than MAX__MAX_PATH_LENGTH.

	// 2006-09-20

	public static float ELEMENTINFO_SCORE_NOT_CALCULATED = -1.0f;
	public static float ELEMENTINFO_SCORE_HOPELESS = -99999.0f;
	// ###should these two be different values?
	public static float BEST_PATH_SCORE_NOT_CALCULATED = -1.0f;
	public static float BEST_PATH_SCORE_BAD = -1.0f;   // ###perhaps not used in real life
	// end 2006-09-20

	Document[] docs;   // package access
	// list of all relevant elements, e.g, <s> elements
	NodeList[] nodes;   // package access. 2004-11-09: flytter denne fra load...thread til hit i model. liste over alle relevante elementer
	// list of all elements, e.g, also <p> elements
	NodeList[] allNodes;   // package access. 2005-09-01. trenger denne fordi: søker etter node med bestemt id. noden kan være på høyere nivå, f.eks <p> i stedet for <s>. og får ikke til å bruke Document.getElementById()

	// ########## skulle vært Hashtable?

	// alignable elements and their ancestors###
	//HashMap relevantElementNames = new HashMap();
	//HashMap relevantAncestorElementNames = new HashMap();
	HashMap<String, Boolean> relevantElementNames = new HashMap<String, Boolean>();   // 2006-11-20
	HashMap<String, Boolean> relevantAncestorElementNames = new HashMap<String, Boolean>();   // 2006-11-20

	private DocumentBuilder builder;

	protected File currentOpenDirectory;
	protected File currentSaveDirectory;

	protected String[] inputFilepath = new String[Alignment.NUM_FILES];
	protected String[] outputFilepath = new String[Alignment.NUM_FILES];
	protected String[] inputFilename = new String[Alignment.NUM_FILES];

	protected String anchorFilename = "";

	protected String settingsFilename = "";   // 2006-09-21

	protected Charset[] charset = new Charset[Alignment.NUM_FILES];   // input files character set. output files character set = input files character set

	protected Aligned aligned;
	protected ToAlign toAlign;
	protected Unaligned unaligned;

	private String specialCharacters   = Alignment.DEFAULT__SPECIAL_CHARACTERS;
	private String scoringCharacters   = Alignment.DEFAULT__SCORING_CHARACTERS;
	private float lengthRatio          = Alignment.DEFAULT__LENGTH_RATIO;
	private int diceMinWordLength      = Alignment.DEFAULT__DICE_MIN_WORD_LENGTH;
	private float diceMinCountingScore = Alignment.DEFAULT__DICE_MIN_COUNTING_SCORE;

	//private int clusterScoreMethod     = Alignment.DEFAULT__CLUSTER_SCORE_METHOD;
	private int largeClusterScorePercentage = Alignment.DEFAULT__LARGE_CLUSTER_SCORE_PERCENTAGE;

	private int maxPathLength          = Alignment.DEFAULT__MAX_PATH_LENGTH;

	//

	private float anchorWordMatchWeight       = Alignment.DEFAULT__ANCHORWORD_MATCH_WEIGHT;
	private float anchorPhraseMatchWeight     = Alignment.DEFAULT__ANCHORPHRASE_MATCH_WEIGHT;
	private float properNameMatchWeight       = Alignment.DEFAULT__PROPERNAME_MATCH_WEIGHT;
	private float diceMatchWeight             = Alignment.DEFAULT__DICE_MATCH_WEIGHT;
	private float dicePhraseMatchWeight       = Alignment.DEFAULT__DICEPHRASE_MATCH_WEIGHT;
	private float numberMatchWeight           = Alignment.DEFAULT__NUMBER_MATCH_WEIGHT;
	private float scoringCharacterMatchWeight = Alignment.DEFAULT__SCORINGCHARACTER_MATCH_WEIGHT;

	// filter for newline format ancestor info
	AncestorFilter ancestorFilter = new AncestorFilter(AncestorFilter.MODE_ALLOW, "", "");  // default = allow none = deny all

	// 2006-02-23 match info log file
	//protected String logFilename = Alignment.DEFAULT__LOG_FILENAME;
	protected String logFilename = "";
	protected OutputStreamWriter logFileOut;
	boolean logging = false;   // logging on/off (true/false)

	protected AnchorWordList anchorWordList;
	protected Compare compare;

	protected MatchInfo matchInfo;   // ### computed at suggest(), but not at unalign()

	public AlignmentModel() {   // package access ¤¤¤ nei dette er jo public

		////System.out.println("går i gang med å lage model");

		// ###hvorfor står disse her? skal de ikke opp blant members?
		setRelevantElementNames(Alignment.DEFAULT__RELEVANT_ELEMENT_NAMES);
		setRelevantAncestorElementNames(Alignment.DEFAULT__RELEVANT_ANCESTOR_ELEMENT_NAMES);

		////System.out.println("skal be om å få laget aligned");
		aligned = new Aligned();
		////System.out.println("skal be om å få laget toAlign");
		toAlign = new ToAlign();
		////System.out.println("skal be om å få laget unaligned");
		unaligned = new Unaligned();
		////System.out.println("har fått laget unaligned");

		docs = new Document[Alignment.NUM_FILES];
		nodes = new NodeList[Alignment.NUM_FILES];
		allNodes = new NodeList[Alignment.NUM_FILES];

		// set up the parser here.
		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		factory.setValidating(false);   // #### være et brukervalg???
		//factory.setValidating(true);
		//factory.setNamespaceAware(true);

		try {
			builder = factory.newDocumentBuilder();
		} catch (ParserConfigurationException pce) {
			// parser with specified options can't be built
			pce.printStackTrace();
		}

		compare = new Compare();

		anchorWordList = new AnchorWordList(AlignmentModel.this);

		matchInfo = new MatchInfo(AlignmentModel.this);

	}

	public void purge(AlignGui gui) {

		// ###dupl kode. se konstruktor.
		// men gir det mening å skille dette ut i en metode,
		// f.eks la konstruktor bruke purge()?
		// #########ikke dupl likevel...

		aligned.purge();
		toAlign.purge();
		unaligned.purge();

		for (int t=0; t<Alignment.NUM_FILES; t++) {
			docs[t]     = null;
			nodes[t]    = null;
			allNodes[t] = null;
		}

		compare.purge();

		matchInfo.purge();

		gui.statusLine.setText("Cleared");

	}

	// input = output files character set.

	// (first and second files may have different character sets,

	// but output character set = input character set)

	public Charset getCharset(int t) {
		return charset[t];
	}

	public void setCharset(int t, Charset cs) {
		charset[t] = cs;
	}

	public void setRelevantElementNames(String string) {

		String[] array = string.split(" ");
		relevantElementNames.clear();   // 2006-02-28. denne manglet
		for (int i=0; i<array.length; i++) {
			String name = array[i];
			if (name != "") {
				relevantElementNames.put(name, true);
			}
		}

	}

	public HashMap getRelevantElementNames() {
		return relevantElementNames;
	}

	public String getRelevantElementNamesAsString() {
		String string = "";
		boolean first = true;
		Iterator it = relevantElementNames.keySet().iterator();
		while (it.hasNext()) {
			if (first) {
				first = false;
			} else {
				string += " ";
			}
			string += (String)it.next();
		}
		return string;
	}

	public void setRelevantAncestorElementNames(String string) {

		String[] array = string.split(" ");
		relevantAncestorElementNames.clear();   // 2006-02-28. denne manglet
		for (int i=0; i<array.length; i++) {
			String name = array[i];
			if (name != "") {
				relevantAncestorElementNames.put(name, true);
			}
		}

	}

	public HashMap getRelevantAncestorElementNames() {
		return relevantAncestorElementNames;
	}

	public String getRelevantAncestorElementNamesAsString() {
		String string = "";
		boolean first = true;
		Iterator it = relevantAncestorElementNames.keySet().iterator();
		while (it.hasNext()) {
			if (first) {
				first = false;
			} else {
				string += " ";
			}
			string += (String)it.next();
		}
		return string;
	}

	public boolean getLogging() {
		//System.out.println("getLogging() kalt. logging = " + logging);
		return logging;
	}

	public void setLogging(boolean logging) {
		this.logging = logging;
	}

	public String getSpecialCharacters() {
		return specialCharacters;
	}

	public void setSpecialCharacters(String specialCharacters) {
		this.specialCharacters = specialCharacters;
	}

	// ### to metoder med samme navn ###
	public String getScoringCharacters() {
		return scoringCharacters;
	}

	public void setScoringCharacters(String scoringCharacters) {
		this.scoringCharacters = scoringCharacters;
	}

	public float getLengthRatio() {
		return lengthRatio;
	}

	public void setLengthRatio(float lengthRatio) {
		this.lengthRatio = lengthRatio;
	}

	public int getDiceMinWordLength() {
		return diceMinWordLength;
	}

	public void setDiceMinWordLength(int diceMinWordLength) {
		this.diceMinWordLength = diceMinWordLength;
	}

	public float getDiceMinCountingScore() {
		return diceMinCountingScore;
	}

	public void setDiceMinCountingScore(float diceMinCountingScore) {
		this.diceMinCountingScore = diceMinCountingScore;
	}

	public int getLargeClusterScorePercentage() {
		return largeClusterScorePercentage;
	}

	public void setLargeClusterScorePercentage(int largeClusterScorePercentage) {
		this.largeClusterScorePercentage = largeClusterScorePercentage;
	}

	//

	public float getAnchorWordMatchWeight() {
		return anchorWordMatchWeight;
	}

	public float getAnchorPhraseMatchWeight() {
		return anchorPhraseMatchWeight;
	}

	public float getProperNameMatchWeight() {
		return properNameMatchWeight;
	}

	public float getDiceMatchWeight() {
		return diceMatchWeight;
	}

	public float getDicePhraseMatchWeight() {
		return dicePhraseMatchWeight;
	}

	public float getNumberMatchWeight() {
		return numberMatchWeight;
	}

	public float getScoringCharacterMatchWeight() {
		return scoringCharacterMatchWeight;
	}

	public void setMatchWeights(
		float anchorWordMatchWeight,
		float anchorPhraseMatchWeight,
		float properNameMatchWeight,
		float diceMatchWeight,
		float dicePhraseMatchWeight,
		float numberMatchWeight,
		float scoringCharacterMatchWeight
	) {
		this.anchorWordMatchWeight       = anchorWordMatchWeight;
		this.anchorPhraseMatchWeight     = anchorPhraseMatchWeight;
		this.properNameMatchWeight       = properNameMatchWeight;
		this.diceMatchWeight             = diceMatchWeight;
		this.dicePhraseMatchWeight       = dicePhraseMatchWeight;
		this.numberMatchWeight           = numberMatchWeight;
		this.scoringCharacterMatchWeight = scoringCharacterMatchWeight;

	}

	// 2006-09-21. ###duplisert, men lager disse for å gjøre det lett for meg selv når jeg nå skal implementere innlesing fra settingsfil ved oppstart

	public void setAnchorWordMatchWeight(float anchorWordMatchWeight) {
		this.anchorWordMatchWeight       = anchorWordMatchWeight;
	}

	public void setAnchorPhraseMatchWeight(float anchorPhraseMatchWeight) {
		this.anchorPhraseMatchWeight     = anchorPhraseMatchWeight;
	}

	public void setProperNameMatchWeight(float properNameMatchWeight) {
		this.properNameMatchWeight       = properNameMatchWeight;
	}

	public void setDiceMatchWeight(float diceMatchWeight) {
		this.diceMatchWeight             = diceMatchWeight;
	}

	public void setDicePhraseMatchWeight(float dicePhraseMatchWeight) {
		this.dicePhraseMatchWeight       = dicePhraseMatchWeight;
	}

	public void setNumberMatchWeight(float numberMatchWeight) {
		this.numberMatchWeight           = numberMatchWeight;
	}

	public void setScoringCharacterMatchWeight(float scoringCharacterMatchWeight) {
		this.scoringCharacterMatchWeight = scoringCharacterMatchWeight;
	}
	// end 2006-09-21

	//

	public int getMaxPathLength() {
		return maxPathLength;
	}

	public void setMaxPathLength(int maxPathLength) {
		this.maxPathLength = maxPathLength;
	}

	public AncestorFilter getAncestorFilter() {
		//System.out.println("getAncestorFilter()");
		return ancestorFilter;
	}

	public void setAncestorInfo(int mode, String elementNames, String attributeNames) {
		//System.out.println("setAncestorInfo(). mode = " + mode);
		setAncestorInfoElementNames(elementNames);
		setAncestorInfoAttributeNames(attributeNames);
		// mode parameter is radio button choice 0-3
		if (mode == AncestorInfoRadioButtonPanel.NONE) {
			ancestorFilter.setMode(AncestorFilter.MODE_ALLOW);
			clearAncestorInfoElementNames();
			clearAncestorInfoAttributeNames();
		} else if (mode == AncestorInfoRadioButtonPanel.ALL) {
			ancestorFilter.setMode(AncestorFilter.MODE_DENY);
			clearAncestorInfoElementNames();
			clearAncestorInfoAttributeNames();
		} else if (mode == AncestorInfoRadioButtonPanel.ALLOW) {
			ancestorFilter.setMode(AncestorFilter.MODE_ALLOW);
		} else if (mode == AncestorInfoRadioButtonPanel.DENY) {
			ancestorFilter.setMode(AncestorFilter.MODE_DENY);
		} else {
			// ### program error ###
			ancestorFilter.setMode(AncestorFilter.MODE_ALLOW);   // ###dodgy??
		}
	}

	// 2006-09-21
	// ###for enkelhets skyld
	public void setAncestorInfoChoice(int mode) {
		// mode parameter is radio button choice 0-3
		if (mode == AncestorInfoRadioButtonPanel.NONE) {
			ancestorFilter.setMode(AncestorFilter.MODE_ALLOW);
			////clearAncestorInfoElementNames();
			////clearAncestorInfoAttributeNames();
		} else if (mode == AncestorInfoRadioButtonPanel.ALL) {
			ancestorFilter.setMode(AncestorFilter.MODE_DENY);
			////clearAncestorInfoElementNames();
			////clearAncestorInfoAttributeNames();
		} else if (mode == AncestorInfoRadioButtonPanel.ALLOW) {
			ancestorFilter.setMode(AncestorFilter.MODE_ALLOW);
		} else if (mode == AncestorInfoRadioButtonPanel.DENY) {
			ancestorFilter.setMode(AncestorFilter.MODE_DENY);
		} else {
			// ### program error ###
			ancestorFilter.setMode(AncestorFilter.MODE_ALLOW);   // ###dodgy??
		}
	}
	// end 2006-09-21

	public int getAncestorInfoChoice() {   // 0 =
		//System.out.println("getAncestorInfoChoice(). ancestorFilter.mode = " + ancestorFilter.mode + ", ancestorFilter.noElements() = " + ancestorFilter.noElements());
		if (ancestorFilter.mode == AncestorFilter.MODE_ALLOW) {
			if (ancestorFilter.noElements()) {
				return AncestorInfoRadioButtonPanel.NONE;   // ###ugly?
			} else {
				return AncestorInfoRadioButtonPanel.ALLOW;   // ###ugly?
			}
		} else {
			if (ancestorFilter.noElements()) {
				return AncestorInfoRadioButtonPanel.ALL;   // ###ugly?
			} else {
				return AncestorInfoRadioButtonPanel.DENY;   // ###ugly?
			}
		}
	}

	public String getAncestorInfoElementNamesAsString() {
		//System.out.println("getAncestorInfoElementNamesAsString()");
		return ancestorFilter.getElementNamesAsString();
	}

	public String getAncestorInfoAttributeNamesAsString() {
		//System.out.println("getAncestorInfoAttributeNamesAsString()");
		return ancestorFilter.getAttributeNamesAsString();
	}

	//private void setAncestorInfoElementNames(String names) {
	public void setAncestorInfoElementNames(String names) {
		//System.out.println("setAncestorInfoElementNames(String names). names = " + names);
		ancestorFilter.setElementNames(names);
	}

	private void clearAncestorInfoElementNames() {

		ancestorFilter.setElementNames("");
	}

	//private void setAncestorInfoAttributeNames(String names) {
	public void setAncestorInfoAttributeNames(String names) {
		//System.out.println("setAncestorInfoAttributeNames(String names). names = " + names);
		ancestorFilter.setAttributeNames(names);
	}

	private void clearAncestorInfoAttributeNames() {
		ancestorFilter.setAttributeNames("");
	}

	// 2006-02-23 match info log file
	public String getLogFilename() {
		return logFilename;
	}

	public void setLogFilename(String logFilename) {
		this.logFilename = logFilename;
	}

	public void setAnchorFilename(String anchorFilename) {
		this.anchorFilename = anchorFilename;
	}

	// 2006-09-21
	public void setSettingsFilename(String settingsFilename) {
		this.settingsFilename = settingsFilename;
	}
	// end 2006-09-21

	
	// end 2006-10-03


	//

    /**
     * ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤Loads an xml file.
     * @return true if loading was successful, false if there was an error.
     *         (most likely a parsing error)
     */
	void loadFile(AlignGui gui, File f, int t) throws Exception {
		gui.statusLine.setText("File -> DOM");
		loadTobeAlignedFile(f, t);
		gui.statusLine.setText("File loaded");
	}

	/*
	 * Added by boerre
	 * Loads an xml file, without gui
	 */
	void loadTobeAlignedFile(File f, int t) throws Exception {
		Document result = null;
		inputFilepath[t] = f.getCanonicalPath();
		inputFilename[t] = f.getName();
		
		try {
			result = builder.parse(f);
			Charset cs = Charset.forName(result.getXmlEncoding());
			setCharset(t, cs);
			docs[t] = result;
		} catch (Exception e) {
			ErrorMessage.error("Exception (1) when loading text " + (t+1) + " " + f.getName() + ":\n" + e.toString());
		}
		
		try {
			nodes[t] = getElements(t);
		} catch (Exception e) {
			throw e;
		}
	
		try {
			allNodes[t] = docs[t].getElementsByTagName("*");
			int elementNumber;
			int numElements = nodes[t].getLength();

			for (elementNumber = 0; elementNumber < numElements; elementNumber++) {

				AElement element = new AElement(nodes[t].item(elementNumber), elementNumber);
				unaligned.add(t, element);
			}

			this.inputFilepath[t] = f.getCanonicalPath();
			this.inputFilename[t] = f.getName();
		} catch (Exception e) {   // ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤
			ErrorMessage.error("Exception (2) when loading text " + (t+1) + " " + f.getName() + ":\n" + e.toString());
		}
	
	}

	private NodeList getElements(int t) throws Exception {
		String[] relevantElementNamesArray = new String[relevantElementNames.size()];
		Iterator it = relevantElementNames.keySet().iterator();
		int count = 0;
		while (it.hasNext()) {
			String name = (String)it.next();
			relevantElementNamesArray[count] = name;
			count++;
		}
        try {   // 2006-09-19
        	return XmlTools.getElementsByTagNames(docs[t], relevantElementNamesArray, getSpecialCharacters());
		} catch (Exception e) {
			throw e;   // ###   // 2006-09-19
		}   // 2006-09-19

	}

    /**
     * establishes corresp attributes in dom for text t
     */
	void setCorrespAttributes(int t) {

    	Iterator it;
    	Iterator eIt;

    	// clean dom of corresp attributes that may have been in the input file

    	for (int i=0; i<((NodeList)(nodes[t])).getLength(); i++) {
			Element el = (Element)(((NodeList)(nodes[t])).item(i));
			el.removeAttribute("corresp");
		}

    	// set new corresp attributes in dom.
    	// loop through all finished alignments

    	String newAttribute;
    	it = aligned.alignments.iterator();
    	while (it.hasNext()) {

			// next alignment
			Link link = (Link)(it.next());
			// get the corresp attribute values from all the other texts.
			// loop through all the other texts
	    	newAttribute = "";
			for (int tt=0; tt<Alignment.NUM_FILES; tt++) {
				if (tt != t) {

					// other text.

					// inspect the elements the alignment has got in this other text
					// and find id's for the corresp attribute to refer to

					if (link.elementNumbers[tt].size() == 0) {

						//System.out.println("t = " + t + ". tt = " + tt + ". the alignment has no elements in this other text");
						// the alignment has no elements in this other text.
						// try to find something else for the corresp attribute to refer to -
						// a node one level up.
						// e.g, let an <s> refer to a <p>.
						// challenge: find the correct <p> (or similar)

						// check with previous siblings -
						// e.g, previous <s>'s in the same <p> -
						// what they refer to in the other text

						// which element to start with?
						//System.out.println("which element to start with?");
						// there might be more than one element from this text in the alignment.
						// find the first one

						int smallestElementNumber = Integer.MAX_VALUE;
						eIt = link.elementNumbers[t].iterator();
						while (eIt.hasNext()) {
							int elementNumber = ((Integer)(eIt.next())).intValue();
							if (elementNumber < smallestElementNumber) {
								smallestElementNumber = elementNumber;
							}
						}

						Node el = nodes[t].item(smallestElementNumber);
						//System.out.println("el. name = " + el.getNodeName() + ". type = " + el.getNodeType() + ". id = " + ((Element)el).getAttribute("id"));

						//System.out.println("look for previous");
						Node prevEl = XmlTools.getPreviousRelevantSiblingElement(el, relevantElementNames);
						String otherId = "";
						while (prevEl != null) {
							//System.out.println("prevEl. name = " + prevEl.getNodeName() + ". type = " + prevEl.getNodeType());
							if (((Element)prevEl).getAttribute("corresp") != "") {

								// found a sibling which refers to #####this other text.
								// get its last corresp attribute value (if more than one)

								String[] values = ((Element)prevEl).getAttribute("corresp").split(" ");
								otherId = values[values.length-1];
								//System.out.println("t = " + t + ". tt = " + tt + ". otherId = " + otherId);
								break;

							} else {

								prevEl = XmlTools.getPreviousRelevantSiblingElement(prevEl, relevantElementNames);

							}
						}
						//System.out.println("otherId = " + otherId);

						if (otherId == "") {

							// no previous sibling refers to the other text.
							//System.out.println("no previous sibling refers to the other text");
							// must try to consult elements in the previous parent element
							//System.out.println("must try to consult elements in the previous parent element");

							// first up one level
							//System.out.println("first up one level");

							Node parent = XmlTools.getRelevantAncestorElement(el, relevantAncestorElementNames);
							if (parent == null) {

								// no higher level.
								//System.out.println("no higher level");
								// no reason to believe there's a higher level in the other text either.
								// refer to nothing

								newAttribute = "";

							} else {

								// then to previous sibling (previous parent)
								//System.out.println("then to previous sibling (previous parent)");

								Node prevParent = XmlTools.getPreviousRelevantSiblingElement(parent, relevantAncestorElementNames);
								if (prevParent == null) {

									// no sibling. first parent.
									//System.out.println("no sibling. first parent");
									// then it's the first parent in the other text we want.
									// first get the first element in the other text

									Node otherElement = nodes[tt].item(0);

									// then get its parent

									Node otherParent = XmlTools.getRelevantAncestorElement(otherElement, relevantAncestorElementNames);
									if (otherParent == null) {

										// no parent.
										// refer to nothing

										newAttribute = "";

									} else {

										// refer to that parent

										newAttribute = ((Element)otherParent).getAttribute("id");
										//System.out.println("refer to that otherParent. t = " + t + ". tt = " + tt + ". newAttribute = " + newAttribute);

									}

								} else {

									// found previous parent.
									//System.out.println("found previous parent");
									// try its children (###which hopefully are on the right level,
									// and not e.g on a level between <p> and <s>).
									// work backwards from last child
									//System.out.println("try its children. work backwards from last child");

									prevEl = XmlTools.getRelevantLastDescendantElement(prevParent, relevantElementNames);
									if (prevEl == null) {

										// no children.
										//System.out.println("no children");
										// could be e.g empty <p>,
										// or e.g some irrelevant element between <p>'s.
										// give up.
										// refer to nothing

										newAttribute = "";

									} else {

										// ...
										//System.out.println("there are children");

										otherId = "";
										while (prevEl != null) {
											//System.out.println("look for child with corresp");
											if (((Element)prevEl).getAttribute("corresp") != "") {

												// found a sibling which refers to #####this other text.
												//System.out.println("found a sibling which refers to #####this other text");
												// get its last corresp attribute value (if more than one)
												//System.out.println("get its last corresp attribute value (if more than one)");

												String[] values = ((Element)prevEl).getAttribute("corresp").split(" ");
												//System.out.println("values.length() = " + values.length() + ", values[0] = " + values[0]);   // ###
												otherId = values[values.length-1];
												//System.out.println("t = " + t + ". tt = " + tt + ". otherId = " + otherId);
												break;

											} else {

												prevEl = XmlTools.getPreviousRelevantSiblingElement(prevEl, relevantElementNames);

											}
										}

										if (otherId == "") {

											// no children of previous parent refer to the other text.
											// ...
											// give up.
											// refer to nothing

											newAttribute = "";

										} else {

											// found reference to the other text
											//System.out.println("found reference to the other text");
											// get element in the other text
											// reference to which level?
											//System.out.println("which level?");

											//Node otherEl = docs[tt].getElementById(otherId);   // ### funker ikke????!!!!
											Node otherEl = XmlTools.getElementByIdInNodeList(allNodes[tt], otherId);  // ### gjør dette isteden

											if (relevantElementNames.containsKey(otherEl.getNodeName())) {

												// the "relevant" level
												//System.out.println("the 'relevant' level");

												// get its parent.
												//System.out.println("get its parent");
												// up one level in the other text

												Node otherParent = XmlTools.getRelevantAncestorElement(otherEl, relevantAncestorElementNames);
												//System.out.println("parent has id = " + ((Element)otherParent).getAttribute("id"));
												if (otherParent == null) {

													// no higher level.
													//System.out.println("no higher level");
													// give up.
													// refer to nothing

													newAttribute = "";

												} else {

													// then to next sibling (next parent)
													//System.out.println("then to next sibling (next parent)");

													Node nextOtherParent = XmlTools.getNextRelevantSiblingElement(otherParent, relevantAncestorElementNames);
													if (nextOtherParent == null) {

														// no next sibling (next parent).
														//System.out.println("no next sibling (next parent)");
														// give up
														// refer to nothing

														newAttribute = "";

													} else {

														// refer to that next sibling (next parent),
														// which hopefully is "in synch"
														// with the current element and its parent

														newAttribute = ((Element)nextOtherParent).getAttribute("id");
														//System.out.println("refer to that next sibling (next parent). t = " + t + ". tt = " + tt + ". newAttribute = " + newAttribute);

													}

												}

											} else {

												// something else, i.e, parent level.
												//System.out.println("something else, i.e, parent level");
												// refer to that parent

												newAttribute = otherId;

											}

										}

									}

								}

							}


						} else {

							// found a previous sibling with a reference to the other text.
							// reference to which level?

							//System.out.println("found a previous sibling with a reference to the other text. otherId = " + otherId);
							//System.out.println("t = " + t);
							//System.out.println("tt = " + tt);
							//System.out.println("docs[tt].getXmlVersion() = " + docs[tt].getXmlVersion());
							//Node otherEl = docs[tt].getElementById(otherId);   // ### funker ikke????!!!!
							Node otherEl = XmlTools.getElementByIdInNodeList(allNodes[tt], otherId);  // ### gjør dette isteden
							//System.out.println("otherEl = " + otherEl);
							//System.out.println("otherEl.getNodeName() = " + otherEl.getNodeName());

							if (relevantElementNames.containsKey(otherEl.getNodeName())) {

								// the "relevant"level

								// get its parent

								Node otherParent = XmlTools.getRelevantAncestorElement(otherEl, relevantAncestorElementNames);

								if (otherParent == null) {

									// has no parent.
									// refer to nothing

									newAttribute = "";

								} else {

									// refer to that parent

									newAttribute = ((Element)otherParent).getAttribute("id");

								}

							} else {

								// something else, i.e, parent level.
								// refer to that parent

								newAttribute = otherId;

							}

						}


					} else {

						// loop through the elements the alignment has got in this other text

						eIt = link.elementNumbers[tt].iterator();
						while (eIt.hasNext()) {
							int elementNumber = ((Integer)(eIt.next())).intValue();
							String id = ((Element)(((AElement)(aligned.elements[tt].get(elementNumber))).element)).getAttribute("id");
							if (newAttribute != "") {
								newAttribute += " ";
							}
							newAttribute += id;
						}

					}

				}
			}

			// set the corresp attribute values in all the elements
			// the alignment has got in the current text
			eIt = link.elementNumbers[t].iterator();
			while (eIt.hasNext()) {
				int elementNumber = ((Integer)(eIt.next())).intValue();
				((Element)(((AElement)(aligned.elements[t].get(elementNumber))).element)).setAttribute("corresp", newAttribute);
			}

		}

	}

    /**
     * Saves an xml file with corresp attributes
     */
    //void saveFile(AlignGui gui, File f, int t) {   // package access
    //void saveFile(File f, int t) {   // package access
    //void saveCorrespFormatFile(File f, int t) {   // package access
    void saveCorrespFormatFile(File f, int t, Charset cs) {   // package access

    	// ¤¤¤ burde vært advarsel hvis pending alignments?
    	// hvis unaligned?
    	// komme spørsmål om prog skal sette et merke?

    	//// establish corresp attributes in dom for text t
    	// ### nei, gjør det på forhånd
    	//setCorrespAttributes(t);

    	// write dom to file

        //XmlOutput.writeXml(docs[t], f);
        XmlOutput.writeXml(docs[t], f, cs);

    }

    /**
     * Saves file in newline format
     */
    void saveNewlineFormatFile(File f, int t, Charset cs, AncestorFilter filter) {   // package access

    	//System.out.println("filter = " + filter);

    	// ¤¤¤ burde vært advarsel hvis pending alignments?
    	// hvis unaligned?
    	// komme spørsmål om prog skal sette et merke?

    	Iterator it;
    	Iterator eIt;

    	// clean dom of corresp attributes

    	for (int i=0; i<((NodeList)(nodes[t])).getLength(); i++) {
			Element el = (Element)(((NodeList)(nodes[t])).item(i));
			el.removeAttribute("corresp");
		}

    	// ...

    	//FileWriter out;
    	OutputStreamWriter out;
    	try {

			//out = new FileWriter(f);
			//¤¤¤endringer 2006-02-20 for å kunne skrive utf-8, o.a
			OutputStream fOut= new FileOutputStream(f);
			OutputStream bOut= new BufferedOutputStream(fOut);
			out = new OutputStreamWriter(bOut, cs);

		} catch (IOException e1) {

			// ### ### ### ### ### ### ### ### ### ### ### ### ###
			Toolkit.getDefaultToolkit().beep();
			System.out.println("Program error? Can't create new FileWriter");
			return;

		}

    	// loop through all finished alignments and write to file

    	it = aligned.alignments.iterator();
    	while (it.hasNext()) {
			// next alignment
			Link link = (Link)(it.next());
			// loop through the alignment's elements
			String line = "";
			boolean first = true;
			eIt = link.elementNumbers[t].iterator();
			while (eIt.hasNext()) {
				int elementNumber = ((Integer)(eIt.next())).intValue();
				AElement aElement = (AElement)(aligned.elements[t].get(elementNumber));
				// ###toNewString(): some users might like parent info prepended to the elements
				// in their newline format output files
				String elementText = aElement.toNewString(filter);
				if (first) {
					first = false;
				} else {
					line += " ";
				}
				line += elementText;
			}
			try {
				out.write(line + "\n");
			} catch (IOException e2) {
				Toolkit.getDefaultToolkit().beep();
				System.out.println("Program error? Can't do out.write");
				try {
					out.close();
				} catch (IOException e3) {
					Toolkit.getDefaultToolkit().beep();
					System.out.println("Program error? Can't do out.close");
					return;
				}
				return;
			}

		}

		try {
			out.close();
		} catch (IOException e4) {
			// ### ### ### ### ### ### ### ### ### ### ### ### ###
			Toolkit.getDefaultToolkit().beep();
			System.out.println("Program error? Can't do out.close");
			return;
		}

    	// what if there are unfinished ones?

    	//...

    }

	/**
	 * Saves file in "external" format
     */
    void saveExternalFormatFile(File f) {

		// ¤¤¤ samme spm som for de andre formatene

		// establish corresp attributes in dom for all texts.
		// ### no - not necessary if already saved in "corresp" format

        OutputStreamWriter out;

        try {

			// output is always utf-8
			OutputStream fOut = new FileOutputStream(f);
			OutputStream bOut = new BufferedOutputStream(fOut);
			Charset cs = Charset.forName("UTF-8");
			out = new OutputStreamWriter(bOut, cs);

		} catch (IOException e) {

			// ¤¤¤ PLAIN_MESSAGE, INFORMATION_MESSAGE, WARNING_MESSAGE, ERROR_MESSAGE?
			JOptionPane.showMessageDialog(
				null,
				"Can't save file " + f.getName(),
				//"¤¤¤Title",
				"Error",   // 2006-09-21
				JOptionPane.ERROR_MESSAGE
			);
            //System.err.println("Exception when saving " + f.getName() + ": ");
            //System.err.println(e.toString());
            ErrorMessage.error("Exception when saving " + f.getName() + ":\n" + e.toString());   // 2006-08-10
            //e.printStackTrace();

            return;

        }

    	// create and output header

    	String data = "<?xml version='1.0' encoding='utf-8'?>\n";
    	// #######mye dupl kode try/except/feilhåndtering
    	try {
			out.write(data, 0, data.length());
		} catch (IOException e) {
			JOptionPane.showMessageDialog(
				null,
				"Can't write to file " + f.getName(),
				//"¤¤¤Title",
				"Error",   // 2006-09-21
				JOptionPane.ERROR_MESSAGE
			);
            //System.err.println("Exception when writing to " + f.getName() + ": ");
            //System.err.println(e.toString());
            ErrorMessage.error("Exception when writing to " + f.getName() + ":\n" + e.toString());   // 2006-08-10
            return;
        }

		// create and output root start element
		//data = "<linkGrp targType='" + "..." + "' toDoc='" + inputFilename[0] + "' fromDoc='" + inputFilename[1] + "'>\n";
		data = "<linkGrp toDoc='" + inputFilename[0] + "' fromDoc='" + inputFilename[1] + "'>\n";   // 2007-01-23
    	try {
			out.write(data, 0, data.length());
		} catch (IOException e) {
			JOptionPane.showMessageDialog(
				null,
				"Can't write to file " + f.getName(),
				//"¤¤¤Title",
				"Error",   // 2006-09-21
				JOptionPane.ERROR_MESSAGE
			);
            //System.err.println("Exception when writing to " + f.getName() + ": ");
            //System.err.println(e.toString());
            ErrorMessage.error("Exception when writing to " + f.getName() + ":\n" + e.toString());   // 2006-08-10
            return;
        }

    	// loop through all finished alignments and write to file

    	Iterator it = aligned.alignments.iterator();
    	while (it.hasNext()) {

			// next alignment.
			// get all the id's to link
			Link link = (Link)(it.next());
			String xtargetsValue = "";
			String typeValue = "";   // 2007-01-23
			// loop through the texts
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				// to get the relevant id's from text t
				// look at the corresp attribute in the alignment's first element in the _other_ text.
				// why do it via the _other_ text?
				// because we may pick up links to elements on a higher level
				int tt = 1 - t;   // ##############
				String ids = "";
				if (link.elementNumbers[tt].size() > 0) {
					int firstElementNumber = ((Integer)(((TreeSet)(link.elementNumbers[tt])).first())).intValue();
					// get the corresp attribute
					//System.out.println((AElement)(aligned.elements[tt].get(firstElementNumber)));
					ids = ((Element)(((AElement)(aligned.elements[tt].get(firstElementNumber))).element)).getAttribute("corresp");
				} else {
					// the alignment has no element in the other text.
					// get the id's from the alignment's elements in _this_ text
					Iterator eIt = link.elementNumbers[t].iterator();
					while (eIt.hasNext()) {
						int elementNumber = ((Integer)(eIt.next())).intValue();
						String id = ((Element)(((AElement)(aligned.elements[t].get(elementNumber))).element)).getAttribute("id");
						if (ids != "") {
							ids += " ";
						}
						ids += id;
					}
				}
				// ...
				if (t > 0) {
					xtargetsValue += ";";
					typeValue += "-";   // 2007-01-23
				}
				xtargetsValue += ids;
				typeValue += "" + link.elementNumbers[t].size();   // 2007-01-23
			}
			// create link (alignment) info
			//data = "<link id='...' xtargets='" + xtargetsValue + "'>\n";
			//data = "<link type='" + typeValue + "' xtargets='" + xtargetsValue + "'>\n";   // 2007-01-23
			data = "<link type='" + typeValue + "' xtargets='" + xtargetsValue + "'/>\n";   // 2010-11-08. stupid error. this is a milestone tag!
			// output info
	    	try {
				out.write(data, 0, data.length());
			} catch (IOException e) {
				JOptionPane.showMessageDialog(
					null,
					"Can't write to file " + f.getName(),
					//"¤¤¤Title",
					"Error",   // 2006-09-21
					JOptionPane.ERROR_MESSAGE
				);
				//System.err.println("Exception when writing to " + f.getName() + ": ");
				//System.err.println(e.toString());
				ErrorMessage.error("Exception when writing to " + f.getName() + ":\n" + e.toString());   // 2006-08-10
				return;
			}

		}

		// create and output root end element

		data = "</linkGrp>\n";
    	try {
			out.write(data, 0, data.length());
		} catch (IOException e) {
			JOptionPane.showMessageDialog(
				null,
				"Can't write to file " + f.getName(),
				//"¤¤¤Title",
				"Error",   // 2006-09-21
				JOptionPane.ERROR_MESSAGE
			);
            //System.err.println("Exception when writing to " + f.getName() + ": ");
            //System.err.println(e.toString());
            ErrorMessage.error("Exception when writing to " + f.getName() + ":\n" + e.toString());   // 2006-08-10
            return;
        }

		// close output file

    	try {
			out.close();
		} catch (IOException e) {
			JOptionPane.showMessageDialog(
				null,
				"Can't close file " + f.getName(),
				//"¤¤¤Title",
				"Error",   // 2006-09-21
				JOptionPane.ERROR_MESSAGE
			);
            //System.err.println("Exception when closing " + f.getName() + ": ");
            //System.err.println(e.toString());
            ErrorMessage.error("Exception when closing " + f.getName() + ":\n" + e.toString());   // 2006-08-10
            return;
        }

	}

    // compute and display info about the current anchor word matches
    // and other matches §§§
    void computeMatches(AlignGui gui) {   // ### compute and display
    //void computeMatches() {
    	//System.out.println("model sin computeMatches(). gui = " + gui);
		matchInfo.computeDisplayableList();
		gui.matchInfoList.setVisible(true);
	}

    // clear info about the current anchor word matches
    // and other matches §§§
    void clearMatches(AlignGui gui) {
		//matchInfoDisplayable.clear();
		//gui.setMatchInfoTextArea("");
		// ### earlier the info box was a JTextArea.
		// now it is a JList referring to a List.
		// it feels wrong to null the List.
		// instead we hide the box
		gui.matchInfoList.setVisible(false);
	}

    // 2006-02-23. log displayed info about the current anchor word matches and other matches §§§
    void logMatches(AlignGui gui) {
		//
		//System.out.println("Skal jeg skrive alignete elementer og match-info til loggfil?");

        if (gui.model.getLogging()) {   // 2006-04-18

			//System.out.println("Ja, jeg skal det.");

			try {

				// ###logMatches() er misvisende navn hvis også skal logge selve elementene

				String text = "";
				for (int t=0; t<Alignment.NUM_FILES; t++) {
					text += "Text " + t + "\n";
					for (Enumeration en = gui.model.toAlign.elements[t].elements(); en.hasMoreElements();) {
						AElement ae = (AElement)en.nextElement();
						int n = ae.elementNumber;
						text += "Element " + n + "\n";
						text += ae.toString() + "\n";
					}
				}
				text += "\n";

				//String text = "log - info:\n" + gui.model.matchInfo.displayableList.toString() + "\n";
				//String text = "";
				for (Enumeration en = gui.model.matchInfo.displayableList.elements(); en.hasMoreElements();) {
					text += (String)en.nextElement() + "\n";
				}
				text += "\n";
				//System.out.println(text);
				logFileOut.write(text, 0, text.length());

			} catch (Exception e) {

				//System.err.println("Exception when writing info to log file");   // ###(vet ikke om jeg har navnet på loggfilen)
				//System.err.println(e.toString());
				ErrorMessage.error("Exception when writing info to log file:\n" + e.toString());   // ###(vet ikke om jeg har navnet på loggfilen)   // 2006-08-10

			}

		}

	}

    // 2006-02-23. put warning in match info log
    //void logMatchesHeader(String header) {   // header or warning
    void logHeader(AlignGui gui, String header) {   // header or warning   // 2006-04-18
		//
		//System.out.println("Skal jeg skrive header eller advarsel til loggfil?");

		if (gui.model.getLogging()) {   // 2006-04-18

			//
			//System.out.println("Ja, jeg skal det.");

			try {

				//String text = "log - warning: " + warning + "\n";
				String text = header + "\n\n";
				//System.out.println(text);
				logFileOut.write(text, 0, text.length());

			} catch (Exception e) {

				//System.err.println("Exception when writing header or warning to log file");   // ###(vet ikke om jeg har navnet på loggfilen)
				//System.err.println(e.toString());
				ErrorMessage.error("Exception when writing header or warning to log file:\n" + e.toString());   // 2006-08-10

			}

		}

	}

	void unalign(AlignGui gui) {   // package access

		// 2006-02-23. put warning in match info log
		//System.out.println("unalign skal kalle logHeader() for å skrive advarsel til loggfil");
		//logMatchesHeader("*** Unalign operation - info above should have been erased ***");
		logHeader(gui, "*** Unalign operation - info above should have been erased ***");   // 2006-04-18

		toAlign.catch_(aligned.drop(gui));

		computeMatches(gui);   // ### compute and display
		//ShowCompare.clear(gui);
		gui.compareInfoPanel.off();
		gui.compareInfoPanel.repaint();
	}

	void align(AlignGui gui, boolean scroll) {   // package access
		// needs to know gui to be able to scroll list boxes for finished alignments

		// 2006-02-23. log displayed info about the current anchor word matches and other matches §§§
		// 2006-02-23. put warning in match info log if more than one alignment
		if (gui.model.toAlign.pendingCount() > 1) {
			//logMatchesHeader("*** More than one alignment - info below is misleading ***");
			logHeader(gui, "*** More than one alignment - info below is misleading ***");   // 2006-04-18
		} else {
			//logMatchesHeader("*** Next alignment ***");
			logHeader(gui, "*** Next alignment ***");   // 2006-04-18
		}

		logMatches(gui);

		aligned.pickUp(toAlign.flush(), scroll);
		// update aligned/total ratio in status line
		gui.statusLine.setMemoryUsage(getMemoryUsage());
		gui.statusLine.setText(gui.model.updateAlignedTotalRatio());

		computeMatches(gui);   // ### compute and display
		gui.compareInfoPanel.off();
		// garbage collect.
		// for each text find number of first element not yet aligned.
		// (if all are aligned the number will be one larger than the highest element number.)
		// (¤¤¤perhaps the code here should check the element numbers themselves and not just rely on size())
		int[] ix = new int[Alignment.NUM_FILES];
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			ix[t] = gui.model.aligned.elements[t].size();
		}
		//System.out.println("align() - before garbage collect");
		Integer mem = getMemoryUsage();
		if (mem.intValue() > 90) {
			System.out.println("S;ppelt;mming");
			compare.garbageCollect(this, ix);
		}
	}

	// ¤¤¤ 2004-10-31. brukes ikke - i hvert fall ikke for øyeblikket
	void link(AlignGui gui, int t, int index, int elementNumber) {   // package access
		// ¤¤¤foreløpig
		//System.out.println("AlignmentModel sin link() med 4 param");
		toAlign.link(gui, t, index, elementNumber);
	}

	// ¤¤¤ 2004-10-31. bare denne brukes.
	// model sin link() kjøres kun når bruker klikker på et element i to-align
	void link(AlignGui gui, int t, int index, int elementNumber, int alignmentNumberToLinkTo) {   // package access
		// ¤¤¤foreløpig
		//System.out.println("AlignmentModel sin link() med 5 param");
		toAlign.link(gui, t, index, elementNumber, alignmentNumberToLinkTo);
	}

	
    
    boolean suggest2WithGui(AlignGui gui) {
        int mode;
        int runLimit;
        
        mode = gui.getMode();
        try {
            runLimit = Integer.parseInt(gui.runLimitTextField.getText());
        } catch (NumberFormatException e) {
            runLimit = 999999;   // ###
        }
        boolean outOfMemory = false;
        int runCount = 0;
        boolean doneAligning = false;
        // loop. do one alignment, or perhaps several alignments (if skip 1-1)
        while (!doneAligning) {
            AlignmentModel.this.compare.resetBestPathScores();   // ¤¤¤¤¤¤¤¤¤¤¤ nå eller etterpå?
            QueueList queueList = lengthenPaths();
            if ((queueList.entry.size() == 0)   // ### will not happen?
                || ((queueList.entry.size() == 1)
                    && (((QueueEntry)(queueList.entry.get(0))).path.steps.size() == 0))) {
                // must be end of all texts
                doneAligning = true;
            } else {
                Path bestPath = getBestPath(queueList);
                
                if (bestPath.steps.size() > 0) {
                    PathStep stepSuggestion = findMoreToAlignWithGui(gui, bestPath);

                    runCount++;
                    doneAligning = getDoneAligning(mode, runCount, runLimit, stepSuggestion);
                    
                    if (!doneAligning) {
                        flushAlignedWithGui(gui);
                    }
                } else {
                    // no best path. reason: no more unaligned text
                    Toolkit.getDefaultToolkit().beep();
                    System.out.println("No more unaligned text");
                    doneAligning = true;
                }
            }
            
            // Short circuit the alignment if we are running out of memory
            if (MemTest.getRemainingHeap() < 1000000) {
                doneAligning = true;
                outOfMemory = true;
            }
        }

        return outOfMemory;
    }

    PathStep findMoreToAlignWithGui(AlignGui gui, Path bestPath) {
        PathStep stepSuggestion = (PathStep)bestPath.steps.get(0);
        for (int t=0; t<Alignment.NUM_FILES; t++) {
            for (int i=0; i<stepSuggestion.increment[t]; i++) {
                toAlign.pickUp(t, unaligned.pop(t));
                updateGuiAfterMore(gui);
            }
        }
        
        return stepSuggestion;
    }
    
    void flushAlignedWithGui(AlignGui gui) {
        // skip mode. automatically align what was suggested
        gui.model.align(gui, false);   // false = don't scroll aligned yet (because of a memory leak - ?)
    }
    
    void updateGui(AlignGui gui) {
        for (int t=0; t<Alignment.NUM_FILES; t++) {
            gui.unalignedScrollPane[t].paintImmediately(0, 0, gui.unalignedScrollPane[t].getWidth(), gui.unalignedScrollPane[t].getHeight());
            gui.alignedScrollPane[t].paintImmediately(0, 0, gui.alignedScrollPane[t].getWidth(), gui.alignedScrollPane[t].getHeight());
            gui.toAlignScrollPane[t].paintImmediately(0, 0, gui.toAlignScrollPane[t].getWidth(), gui.toAlignScrollPane[t].getHeight());
        }

        computeMatches(gui);   // ### compute and display

        gui.compareInfoPanel.on();
        gui.compareInfoPanel.repaint();
    }
        
    void updateAlignedView(AlignGui gui) {
        for (int t=0; t<Alignment.NUM_FILES; t++) {
            gui.alignedListBox[t].ensureIndexIsVisible(aligned.elements[t].getSize()-1);
        }
    }
    
    // ### ikke godt navn? i skip-1-1-modus og automatisk gjør den mer enn bare å foreslå
	void suggest(AlignGui gui) {
		boolean outOfMemory = false;

        if (!toAlign.empty()) {
            // automatically align before suggesting
            align(gui, false);   // false = don't scroll aligned yet (because of a memory leak - ?)
        }
    
        if (!toAlign.empty()) {
            Toolkit.getDefaultToolkit().beep();
        } else {
            outOfMemory = suggest2WithGui(gui);
            updateGui(gui);
        }
        // scroll aligned. (waited until now because of a memory leak - ?)
        updateAlignedView(gui);
        if (outOfMemory) {
            JOptionPane.showMessageDialog(
                null,
                "Running out of memory.\n",
                "Running out of memory",
                JOptionPane.ERROR_MESSAGE
            );
        }

        System.gc();
	}

	void skipCorresp(AlignGui gui) {

		// the texts may contain some alignments already - in the form of corresp attributes.
		// if so, link them together, according to the corresp values,
		// and get them up into aligned area,
		// until we run out of matching corresp values.
		// ### to-align must be empty and the starts of unaligned must be in synch

		// ##### hadde vært tøft om de viste med farger allerede i unaligned????????????

		System.out.println("enter skipCorresp()");

		// is to-align empty?
		if (!toAlign.empty()) {
			// no. ######### trenger bedre advarsel/forklaring for brukeren enn kun et pip
			Toolkit.getDefaultToolkit().beep();
			System.out.println("Can't do this while there are pending alignments");
		} else {

			System.out.println("to-align is empty");
			AElement aEl;
			Element element;
			AlignmentsEtc someAligned;
			int alignmentNumber = 0;
			int t, tt, t2;
			Link link;

			int holeyCount = 0;

			// for each text continue as long as there are elements,
			// and the elements have ''corresp'' attributes.
			// initialize the thing that keeps track of which texts
			// have run out of relevant elements.
			boolean[] stop = new boolean[Alignment.NUM_FILES];
			for (t=0; t<Alignment.NUM_FILES; t++) {
				stop[t] = false;
			}

			// for each

			// make a new empty someAligned.
			// will be filled and emptied and reused. ###thrown away
			someAligned = new AlignmentsEtc();
			//System.out.println("make a new empty someAligned");

			// ...

			boolean done = false;
			do {

				System.out.println("find the elements belonging to the next alignment, i.e, find the corresponding elements in each text, ...");
				// find the elements belonging to the next alignment,
				// i.e, find the corresponding elements in each text,
				// from the unaligned areas.
				// what about loners?
				// all right. they might need special treatment.
				// what about crossing relations?
				// oh yes. if relations cross we have to continue and find more alignments,
				// until they make a continuous glob without any holes

				System.out.println("first skim off all loners lying topmost in the unaligned.");
				// first skim off all loners lying topmost in the unaligned.
				// take them from the left

				for (t=0; t<Alignment.NUM_FILES; t++) {

					if (!stop[t]) {

						tt = 1 - t;   // ###
						System.out.println("text " + t + ". other text is " + tt);

						System.out.println("loop just in case there are several loners in a row in the same text");
						// loop just in case there are several loners in a row in the same text
						boolean finishedLonersInThisText = false;
						do {

							System.out.println("try to get loner from text " + t);
							// try to get loner from text t.
							// stop text t if no element or no corresp

							if (unaligned.elements[t].size() == 0) {

								System.out.println("no more unaligned elements in text " + t + ". stop text " + t);
								stop[t] = true;
								finishedLonersInThisText = true;

							} else {

								System.out.println("1 get next available element in text " + t);
								// get next available element in text t #########
								//element = (Element)((AElement)(unaligned.elements[t].get(0))).element;
								aEl = Skip.getNextAvailableUnalignedElement(unaligned, someAligned, t);
								System.out.println("1");
								element = (Element)aEl.element;
								System.out.println("2");
								System.out.println(element.getAttributes());
								System.out.println(element.getAttributes().getNamedItem("corresp"));
								// 2006-09-15 ###dupl. kode
								String correspValue;   // 2006-09-15
								if (element.getAttributes().getNamedItem("corresp") == null) {   // 2006-09-15
									correspValue = "";   // 2006-09-15
								} else {   // 2006-09-15
									//String correspValue = element.getAttributes().getNamedItem("corresp").getNodeValue();
									correspValue = element.getAttributes().getNamedItem("corresp").getNodeValue();   // 2006-09-15
								}   // 2006-09-15
								System.out.println("topmost unaligned element 1. correspValue = " + correspValue);
								if (correspValue == "") {

									System.out.println("(I) element with no corresp attribute. stop text " + t);
									// element with no corresp attribute
									stop[t] = true;
									finishedLonersInThisText = true;

								} else {

									System.out.println("there are id(s) in the corresp attribute of the element");
									// there are id(s) in the corresp attribute of the element
									String[] correspIds = correspValue.split(" ");
									if (correspIds.length > 1) {
										System.out.println("more than one id. this element can't be a loner.");
										// more than one id. this element can't be a loner.
										// loners refer to one element only, on a "parent" level
										finishedLonersInThisText = true;
									} else {
										System.out.println("one id. check alignable elements in the other text to see if the id belongs to one of them");
										// one id. check alignable elements in the other text
										// to see if the id belongs to one of them
										if (XmlTools.getElementByIdInNodeList(nodes[tt], correspValue) != null) {
											System.out.println("belongs to alignable element in other text. => not loner");
											// belongs to alignable element in other text.
											// => not loner
											// check further
											if (XmlTools.getElementByIdInDefaultListModel(unaligned.elements[tt], correspValue) != null) {
												// the element in the other text is an unaligned element
												// ok
												finishedLonersInThisText = true;
											} else {
												System.out.println("error in corresp. treat as loner");
												// the element in the other text is not an unaligned element
												// error in corresp
												//###############
												// treat as loner
											}
										} else if(XmlTools.getElementByIdInNodeList(allNodes[tt], correspValue) != null) {
											System.out.println("belongs to other element in other text, presumably one on a 'parent' level. => loner");
											// belongs to other element in other text,
											// presumably one on a "parent" level.
											// (¤¤¤but we don't check that element further,.
											// neither its "level" nor its location)
											// => loner
										} else {
											System.out.println("error in file. treat as loner");
											// error in file.
											//###############
											// treat as loner
										}
									}

									// ...
									System.out.println("xxx");

									if (!finishedLonersInThisText) {
										System.out.println("found loner. pop it from unaligned and make an alignment out of it");
										// found loner.
										//// pop it from unaligned and make an alignment out of it
										// make an alignment out of it
										//AElement aEl = (AElement)(AlignmentModel.this.unaligned.pop(t));
										System.out.println("1.5 get next available element in text " + t);
										// get next available element in text t #########
										//AElement aEl = (AElement)(unaligned.elements[t].get(0));
										aEl = Skip.getNextAvailableUnalignedElement(unaligned, someAligned, t);
										link = new Link();
										link.alignmentNumber = alignmentNumber;
										aEl.alignmentNumber = link.alignmentNumber;
										alignmentNumber++;
										//link.elementNumbers[t] = new TreeSet();
										link.elementNumbers[t] = new TreeSet<Integer>();   // 2006-11-20
										link.elementNumbers[t].add(aEl.elementNumber);
										//link.elementNumbers[tt] = new TreeSet();
										link.elementNumbers[tt] = new TreeSet<Integer>();   // 2006-11-20
										// add it to our collection of ... alignments (the someAligned thing)
										someAligned.add(link);
										//someAligned.print();
										//if (someAligned.alignments.size() > 3) {
										//	System.out.println("kill this process"); stop[0] = true; stop[1] = true; finishedLonersInThisText = true;
										//}
										// ###also the element. kunne ikke Link også holdt rede på disse?
										//someAligned.add(t, element);
										someAligned.add(t, aEl);
										//someAligned.print();
										if (!someAligned.hasHoles()) {
											// got one or more alignments, with no holes.
											// pop the relevant elements out of unaligned.
											// we don't need their content.
											// we got all the data we need already.
											// just throw them away
											System.out.println("pop and throw them away 1");
											for (t2=0; t2<Alignment.NUM_FILES; t2++) {
												for (int i=0; i<((DefaultListModel)someAligned.elements[t2]).size(); i++) {
													System.out.println("pops from text " + t2);
													AElement aDum = (AElement)(AlignmentModel.this.unaligned.pop(t2));
													String id = aDum.element.getAttributes().getNamedItem("id").getNodeValue();
													System.out.println("popped element with id " + id + " from text " + t2);
													///////////MemTest.print("Heap memory");
													//System.out.println("A");
													//MemTest.print("Tenured Gen", "");
													//System.out.println("unaligned.elements[" + t2+ "].size() = " + unaligned.elements[t2].size());
												}
											}
											// process the someAligned and empty it
											System.out.println("process the someAligned and empty it 1");
											toAlign.catch_(someAligned);
											someAligned = new AlignmentsEtc();
											aligned.pickUp(toAlign.flush(), false);   // false = don't scroll aligned yet (because of a memory leak - ?)
											System.out.println("another use of pickup 1953");
											// update aligned/total ratio in status line
											gui.statusLine.setMemoryUsage(getMemoryUsage());
											gui.statusLine.setText(updateAlignedTotalRatio());
											holeyCount = 0;
										} else {
											holeyCount++;
											System.out.println("holes 1");
										}
									}

								}
							}
						} while (!finishedLonersInThisText);

					}

				} // for

				/// then ...
				System.out.println("finished skimming loners");

				if (!(stop[0] && stop[1])) {   // ###

					// not run out of elements with corresp

					System.out.println("grab the leftmost topmost element");
					// grab the leftmost topmost element
					// of a more substantial alignment (i.e, not loner)

					link = new Link();
					link.alignmentNumber = alignmentNumber;
					alignmentNumber++;
					t = 0;
					tt = 1;
					System.out.println("get top element in text " + t);
					// get top element in text t.
					// stop text t if no element or no corresp
					if (unaligned.elements[t].size() == 0) {

						System.out.println("no more unaligned elements in text " + t + ". stop text " + t);

						stop[t] = true;

					} else {

						System.out.println("2 get next available element in text " + t);
						// get next available element in text t #########
						//AElement aEl = (AElement)(unaligned.elements[t].get(0));
						aEl = Skip.getNextAvailableUnalignedElement(unaligned, someAligned, t);
						element = (Element)aEl.element;
						// 2006-09-15 ###dupl. kode
						String correspValue;   // 2006-09-15
						if (element.getAttributes().getNamedItem("corresp") == null) {   // 2006-09-15
							correspValue = "";   // 2006-09-15
						} else {   // 2006-09-15
							//String correspValue = element.getAttributes().getNamedItem("corresp").getNodeValue();
							correspValue = element.getAttributes().getNamedItem("corresp").getNodeValue();   // 2006-09-15
						}   // 2006-09-15
						System.out.println("topmost unaligned element 2. correspValue = " + correspValue);
						if (correspValue == "") {

							System.out.println("(II) element with no corresp attribute. stop text " + t);
							// element with no corresp attribute
							stop[t] = true;

						} else {

							System.out.println("there are id(s) in the corresp attribute of the element");
							// there are id(s) in the corresp attribute of the element
							//link.alignmentNumber = alignmentNumber;
							link.elementNumbers[t] = new TreeSet();
							link.elementNumbers[t].add(aEl.elementNumber);
							link.elementNumbers[tt] = new TreeSet();
							// ###also ...
							//someAligned.add(t, element);
							aEl.alignmentNumber = link.alignmentNumber;
							someAligned.add(t, aEl);
							//someAligned.print();
							System.out.println("get all the corresponding elements in the other text.");
							// get all the corresponding elements in the other text.
							String[] correspIds = correspValue.split(" ");
							AElement otherAEl = null;
							for (int i = 0; i < correspIds.length; i++) {
								System.out.println("get Node otherEl");
								Node otherEl = XmlTools.getElementByIdInNodeList(nodes[tt], correspIds[i]);
								if (otherEl != null) {
									System.out.println("the corresp id makes sense insofar as it is an id for an alignable element in the other text.");
									// the corresp id makes sense insofar as
									// it is an id for an alignable element in the other text.
									// check further
									otherAEl = AlignmentModel.this.unaligned.get(tt, otherEl);
									if (otherAEl != null) {
										System.out.println("it's an unaligned element all right");
										// it's an unaligned element all right
										link.elementNumbers[tt].add(otherAEl.elementNumber);
										// ###also ...
										//someAligned.add(tt, (Element)otherAEl.element);
										otherAEl.alignmentNumber = link.alignmentNumber;
										someAligned.add(tt, otherAEl);
										//someAligned.print();
									} else {
										System.out.println("error");
										// error
										// ######### trenger feilmelding - ikke kun et pip?
										Toolkit.getDefaultToolkit().beep();
										System.out.println("Hit a case the program can't handle");
										// ####grisete
										stop[0] = true;
										stop[1] = true;
										break;
									}
								}
							}
							if (!(stop[0] && stop[1])) {   // ###
								System.out.println("take one of these elements in the other text and get all the corresponding elements in the first text");
								System.out.println("otherAEl = " + otherAEl);
								// take one of these elements in the other text and get
								// all the corresponding elements in the first text
								String backCorrespValue = otherAEl.element.getAttributes().getNamedItem("corresp").getNodeValue();
								System.out.println("backCorrespValue = " + backCorrespValue);
								String[] backCorrespIds = backCorrespValue.split(" ");
								for (int i = 0; i < backCorrespIds.length; i++) {
									System.out.println("get Node backEl");
									Node backEl = XmlTools.getElementByIdInNodeList(nodes[t], backCorrespIds[i]);
									if ( backEl != null) {
										System.out.println("the ... id makes sense insofar as it is an id for an alignable element in the first text.");
										// the .. id makes sense insofar as
										// it is an id for an alignable element in this text.
										// check further
										AElement backAEl = AlignmentModel.this.unaligned.get(t, backEl);
										if (backAEl != null) {
											System.out.println("it's an unaligned element all right");
											// it's an unaligned element all right
											link.elementNumbers[t].add(backAEl.elementNumber);
											// ###also ...
											//someAligned.add(t, (Element)backAEl.element);
											backAEl.alignmentNumber = link.alignmentNumber;
											someAligned.add(t, backAEl);
											//someAligned.print();
										} else {
											System.out.println("error");
											// error
											// ######### trenger feilmelding - ikke kun et pip?
											Toolkit.getDefaultToolkit().beep();
											System.out.println("Hit a case the program can't handle");
											// ####grisete
											stop[0] = true;
											stop[1] = true;
											break;
										}
									}
								}
							}
							if (!(stop[0] && stop[1])) {   // ###
								// ??? stop text t if no element or no corresp
								// check both sides to see if all the corresp''s agree
								//if link.consistentCorresp() { ##################################i.g.n.m. I.G.N.M.
									// we have made Link out of them.
									// put it in a new someAligned
									someAligned.add(link);
									//someAligned.print();
									//if (someAligned.alignments.size() > 3) {
									//	System.out.println("kill this process"); stop[0] = true; stop[1] = true;
									//}
									if (!someAligned.hasHoles()) {
										// got one or more alignments, with no holes.
										// pop the relevant elements out of unaligned.
										// we don't need their content.
										// we got all the data we need already.
										// just throw them away
										System.out.println("pop and throw them away 2");
										for (t2=0; t2<Alignment.NUM_FILES; t2++) {
											for (int i=0; i<((DefaultListModel)someAligned.elements[t2]).size(); i++) {
												System.out.println("pops from text " + t2);
												AElement aDum = (AElement)(AlignmentModel.this.unaligned.pop(t2));
												String id = aDum.element.getAttributes().getNamedItem("id").getNodeValue();
												System.out.println("popped element with id " + id + " from text " + t2);
												///////////MemTest.print("Heap memory");
												//System.out.println("B");
												//MemTest.print("Tenured Gen", "");
												//System.out.println("unaligned.elements[" + t2+ "].size() = " + unaligned.elements[t2].size());
											}
										}
										//System.out.println("B2");
										//MemTest.print("Tenured Gen", "");
										// process the someAligned and empty it
										System.out.println("process the someAligned and empty it 2");
										toAlign.catch_(someAligned);
										//System.out.println("B3");
										//MemTest.print("Tenured Gen", "");
										someAligned = new AlignmentsEtc();
										//System.out.println("B5");
										//MemTest.print("Tenured Gen", "");
										aligned.pickUp(toAlign.flush(), false);   // false = don't scroll aligned yet (because of a memory leak - ?)
										System.out.println("another use of pickup 1948");
										// update aligned/total ratio in status line
										gui.statusLine.setMemoryUsage(getMemoryUsage());
										gui.statusLine.setText(updateAlignedTotalRatio());

										//System.out.println("B6");
										//MemTest.print("Tenured Gen", "");
										holeyCount = 0;
										//System.out.println("B7");
										//MemTest.print("Tenured Gen", "");
									} else {
										holeyCount++;
										System.out.println("holes 2");
									}
									System.out.println("B8");
									//MemTest.print("Tenured Gen", "");
								//} else {
								//	error
								//}
							}
							System.out.println("C");
							//MemTest.print("Tenured Gen", "");
						}
						System.out.println("D");
						//MemTest.print("Tenured Gen", "");
					}
					System.out.println("E");
					//MemTest.print("Tenured Gen", "");

				}
				System.out.println("F");
				//MemTest.print("Tenured Gen", "");

				if (holeyCount > 10) {
					// we have done ... alignments, and someAligned is still holey.
					// we suspect something is wrong
					System.out.println("kill this process"); stop[0] = true; stop[1] = true;
				}

				System.out.println("før while. stop[0]=" + stop[0] +", stop[1]=" + stop[1]);

			} while(!(stop[0] && stop[1]));
			System.out.println("G");
			//MemTest.print("Tenured Gen", "");

			if (!someAligned.empty()) {
				// error
				// ######### trenger feilmelding - ikke kun et pip?
				//dette blir ikke bra hvis someAligned har hull!!! ########################
				Toolkit.getDefaultToolkit().beep();
				System.out.println("!someAligned.empty()");
				System.out.println("Dodgy case??????????????");
				toAlign.catch_(someAligned);
				someAligned = new AlignmentsEtc();
			}

		}

		// scroll aligned. (waited until now because of a memory leak - ?)
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			gui.alignedListBox[t].ensureIndexIsVisible(aligned.elements[t].getSize()-1);
		}

	}

	// 2006-08-15

	void break_(AlignGui gui) {
		Toolkit.getDefaultToolkit().beep();
	}
	// end 2006-08-15

	void less(AlignGui gui, int t) {   // package access

		////System.out.println("at model.less()");
		//unaligned.catch_(t, toAlign.drop(t));
		unaligned.catch_(t, toAlign.drop(gui, t));   // ### 2006-03-30
		computeMatches(gui);   // ### compute and display
		//ShowCompare.clear(gui);
		gui.compareInfoPanel.off();
		gui.compareInfoPanel.repaint();

		
		// update aligned/total ratio in status line
		gui.statusLine.setMemoryUsage(getMemoryUsage());
		gui.statusLine.setText(updateAlignedTotalRatio());

	}

	void saveFilesAutomatically() {
			// establish corresp attributes in dom for all texts.
			// methods for saving in "corresp" and "external" formats depend on this
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				setCorrespAttributes(t);
			}

			File tempPath;
			String outputFilenameSuggestion;
			String path = "";
			File outputFilepathSuggestion;
			int returnVal;

			// save in "external" format
			// the basis for the suggestion is the input file paths
			outputFilenameSuggestion = "";
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				tempPath = new File(inputFilepath[t]);
				path = tempPath.getParent();
				String tempFilename = tempPath.getName();
				if (outputFilenameSuggestion != "") {
					outputFilenameSuggestion += "_";
				}
				outputFilenameSuggestion += ExtensionUtils.getFilenameWithoutExtension(tempFilename);
			}
			outputFilenameSuggestion = path + "/" + outputFilenameSuggestion + ".xml";
			outputFilepathSuggestion = new File(outputFilenameSuggestion);
			saveExternalFormatFile(outputFilepathSuggestion);
			for (int t=0; t<Alignment.NUM_FILES; t++) {

				// the basis for the suggestion is the input file path
				tempPath = new File(inputFilepath[t]);
				String tempFilename = tempPath.getName();

				for (int fi=0; fi<2; fi++) {

					if (fi == 0) {
// 						outputFilenameSuggestion = ExtensionUtils.appendName(tempFilename, "_cor");
					} else {
						// save in newline format
						outputFilenameSuggestion = ExtensionUtils.changeExtension(ExtensionUtils.appendName(tempFilename, "_new"), "txt");   // ### ¤¤¤ ###########
					}

					if (fi == 0) {
						// save in corresp format
// 						outputFilenameSuggestion = path + "/" + outputFilenameSuggestion;
// 						outputFilepathSuggestion = new File(outputFilenameSuggestion);
// 						saveCorrespFormatFile(outputFilepathSuggestion, t, getCharset(t));
					} else {
						// save in newline format
						outputFilenameSuggestion = path + "/" + outputFilenameSuggestion;
						outputFilepathSuggestion = new File(outputFilenameSuggestion);
						saveNewlineFormatFile(outputFilepathSuggestion, t, getCharset(t), getAncestorFilter());
					}
					
				}
			}
		
	}

	void updateGuiAfterMore(AlignGui gui) {   // package access
		computeMatches(gui);   // ### compute and display);
		gui.compareInfoPanel.off();
		gui.compareInfoPanel.repaint();
		
		// update aligned/total ratio in status line
		gui.statusLine.setMemoryUsage(getMemoryUsage());
		gui.statusLine.setText(updateAlignedTotalRatio());
	}

/*
From here on: Functions that are used by suggestWithoutGui
*/

    // ### ikke godt navn? i skip-1-1-modus og automatisk gjør den mer enn bare å foreslå
    void suggestWithoutGui() {
        boolean outOfMemory = false;
        
        if (!toAlign.empty()) {
            suggest1();
        }
    
        if (toAlign.empty()) {
            outOfMemory = suggest2WithoutGui();
        }
        
        if (outOfMemory) {
            System.out.println("Running out of memory");
        }

        System.gc();
    }

    void suggest1() {
        aligned.pickUp(toAlign.flush(), false);
        int[] ix = new int[Alignment.NUM_FILES];
        for (int t=0; t<Alignment.NUM_FILES; t++) {
            ix[t] = aligned.elements[t].size();
        }
        //System.out.println("align() - before garbage collect");
        Integer mem = getMemoryUsage();
        if (mem.intValue() > 90) {
            System.out.println("S;ppelt;mming");
            compare.garbageCollect(this, ix);
        }
    }
    
    boolean suggest2WithoutGui() {
        int mode;
        int runLimit;
        boolean outOfMemory = false;

        mode = Alignment.MODE_AUTO;
        runLimit = 999999;
        
        int runCount = 0;
        boolean doneAligning = false;
        // loop. do one alignment, or perhaps several alignments (if skip 1-1)
        while (!doneAligning) {
            AlignmentModel.this.compare.resetBestPathScores();   // ¤¤¤¤¤¤¤¤¤¤¤ nå eller etterpå?
            QueueList queueList = lengthenPaths();
            if ((queueList.entry.size() == 0)   // ### will not happen?
                || ((queueList.entry.size() == 1)
                    && (((QueueEntry)(queueList.entry.get(0))).path.steps.size() == 0))) {
                // must be end of all texts
                doneAligning = true;
            } else {
                Path bestPath = getBestPath(queueList);
                
                if (bestPath.steps.size() > 0) {
                    PathStep stepSuggestion = findMoreToAlignWithoutGui(bestPath);

                    runCount++;
                    doneAligning = getDoneAligning(mode, runCount, runLimit, stepSuggestion);
                    
                    if (!doneAligning) {
                        flushAlignedWithoutGui();
                    }
                } else {
                    System.out.println("No more unaligned text");
                    doneAligning = true;
                }
            }
            
            // Short circuit the alignment if we are running out of memory
            if (MemTest.getRemainingHeap() < 1000000) {
                doneAligning = true;
                outOfMemory = true;
            }
        }

        return outOfMemory;
    }
    
    // will investigate "all" possible paths with a certain number of steps.
    // will loop once per step, each time building "all" paths
    // that are one step longer than in the previous loop.
    // collect the paths in the queue list.
    // init queue list (queueList)
    QueueList lengthenPaths() {
        // start 1 before first unaligned elements ¤¤¤
        int[] position = findStartPosition();
            
        QueueList queueList = new QueueList(AlignmentModel.this, position);
        // the paths that are one step longer will, while they are being created,
        // reside in nextQueueList
        QueueList nextQueueList;
        // variable for each of all the possible steps to try when lengthening a path: 0-0, 0-1, etc
        // init counter for the lengthening loop
        int stepCount = 0;
        // the lengthening loop
        boolean doneLengthening = false;
        do {
            Iterator qIt = queueList.entry.iterator();
            nextQueueList = new QueueList();
            // loop over each entry in the queue list. each entry is a path
            while (qIt.hasNext()) {
                Object temp = qIt.next();
                QueueEntry queueEntry = (QueueEntry)(temp);
                if (!queueEntry.removed) {   // ### 2005-11-02. hmmm. denne var det ikke så mye vits så lenge jeg ikke merket for fjerning i queueList, bare i nextQueueList
                    if (queueEntry.end) {
                        // path goes to the end of all texts.
                        // use as it is
                        QueueEntry newQueueEntry = (QueueEntry)queueEntry.clone();   // denne har allerede newQueueEntry.end = true;
                    } else {
                        lengthenCurrentPath(queueEntry, queueList, nextQueueList);
                    }
                }
            }
            nextQueueList.removeForReal();   // remove for real. see above
            if (nextQueueList.empty()) {
                // not possible to lengthen path. must have reached the end of all the texts
                doneLengthening = true;
            } else {
                queueList = nextQueueList;
                stepCount++;
                doneLengthening = (stepCount >= AlignmentModel.this.getMaxPathLength());
            }
        } while (!doneLengthening);
        
        return queueList;
    }
    
    Path getBestPath(QueueList queueList) {
        Iterator qIt2 = queueList.entry.iterator();
        // normalized = divided by number of sentences.
        // done because: the paths compared may well have the same number of steps,
        // but they often have a different number of sentences.
        // if not normalized a path with e.g 2-1 + 1-2 can win over a correct 1-1 + 1-1 + 1-1
        // because it gains extra points from the extra sentences the former path has at its end
        float normalizedBestScore = AlignmentModel.BEST_PATH_SCORE_NOT_CALCULATED;   // 2006-09-20
        Path bestPath = null;
        while (qIt2.hasNext()) {
            QueueEntry candidate = ((QueueEntry)qIt2.next());
            float normalizedCandidateScore = candidate.score / candidate.path.getLengthInSentences();
            if (normalizedCandidateScore > normalizedBestScore) {
                normalizedBestScore = normalizedCandidateScore;
                bestPath = candidate.path;
            }
        }
        
        return bestPath;
    }
    
    PathStep findMoreToAlignWithoutGui(Path bestPath) {
        PathStep stepSuggestion = (PathStep)bestPath.steps.get(0);
        for (int t=0; t<Alignment.NUM_FILES; t++) {
            for (int i=0; i<stepSuggestion.increment[t]; i++) {
                toAlign.pickUp(t, unaligned.pop(t));
                System.out.println(updateAlignedTotalRatio());
                System.out.println("Memory used: " + getMemoryUsage() + "%");
            }
        }
        
        return stepSuggestion;
    }
    
    boolean getDoneAligning(int mode, int runCount, int runLimit, PathStep stepSuggestion) {
        boolean doneAligning = false;
        
        if (mode == Alignment.MODE_ONE) {
            doneAligning = true;
        } else if (mode == Alignment.MODE_AUTO) {
            if (runCount < runLimit) {
                doneAligning = false;
            } else {
                doneAligning = true;
            }
        } else if (mode == Alignment.MODE_SKIP11) {
            if ((runCount < runLimit) && stepSuggestion.is11()) {
                doneAligning = false;
            } else {
                doneAligning = true;
            }
        }
        
        return doneAligning;
    }
    
    void flushAlignedWithoutGui() {
        int[] ix = new int[Alignment.NUM_FILES];

        aligned.pickUp(toAlign.flush(), false);
        for (int t=0; t<Alignment.NUM_FILES; t++) {
            ix[t] = aligned.elements[t].size();
        }
        //System.out.println("align() - before garbage collect");
        Integer mem = getMemoryUsage();
        if (mem.intValue() > 90) {
//             System.out.println("S;ppelt;mming");
            compare.garbageCollect(this, ix);
        }
    }
    
    Integer getMemoryUsage() {
        //System.out.println("model sin setMemoryUsage()");
        long[] array = MemTest.getMemoryUsage();
        long max  = array[0];
        long used = array[1];
        return Math.round((float)((float)(used) / max * 100.0));
    }
    
    int[] findStartPosition() {
        int[] position = new int[Alignment.NUM_FILES];
        for (int t=0; t<Alignment.NUM_FILES; t++) {
            
            if (((DefaultListModel)(unaligned.elements[t])).size() > 0) {
                position[t] = ((AElement)(((DefaultListModel)(unaligned.elements[t])).get(0))).elementNumber - 1;
            } else {
                // no more unaligned elements in text t.
                position[t] = AlignmentModel.this.nodes[t].getLength() - 1;
            }
        }
        
        return position;
    }
    
    void lengthenCurrentPath(QueueEntry queueEntry, QueueList queueList, QueueList nextQueueList) {
        // loop through all the possible steps to lengthen the current path with.
        // note. some or all of these steps will not be possible after all
        // at the end of the texts
        Iterator iIt = AlignmentModel.this.compare.stepList.iterator();
        while (iIt.hasNext()) {
            PathStep step = (PathStep)iIt.next();
            try {
                QueueEntry newQueueEntry = queueEntry.makeLongerPath(AlignmentModel.this, step);
                if (newQueueEntry.path != null) {   // ¤¤¤ .path = null er min krøkkete måte å fortelle at det nye forslaget til path ikke er bedre enn andre paths til samme position, og at forslaget skal kastes
                    // this new path might be a better (better-scoring) path than
                    // some other paths in the new list. remove those other paths, if any
                    int[] pos = newQueueEntry.path.position;
                    nextQueueList.remove(pos);   // doesn't remove them for real. just marks them for removal later
                    queueList.remove(pos);   // must do the same thing in the source. (###dodgy?) see comments for the QueueList remove() method
                    // insert new path in the new list
                    nextQueueList.add(newQueueEntry);
                }
            } catch (EndOfAllTextsException e) {
                // end of all texts.
                // use path as it is, but mark it properly
                QueueEntry newQueueEntry = (QueueEntry)queueEntry.clone();
                newQueueEntry.end = true;
                // insert new path in the new list unless already there.
                if (!nextQueueList.contains(newQueueEntry)) {
                    nextQueueList.add(newQueueEntry);
                }
            } catch (EndOfTextException e) {
                // end of at least one text but not all of them.
                // forget
            } catch (BlockedException e) {
                //...
            }
        }
    }
    
    String updateAlignedTotalRatio() {
        String text = "Aligned: ";
        for (int t=0; t<Alignment.NUM_FILES; t++) {
            if (t > 0) { text += " - "; }
            text += Integer.toString(getLowestUnalignedElementNumber(t) + 1) + "/" + nodes[t].getLength();
        }
        return text;
    }
    
    int getLowestUnalignedElementNumber(int t) {

        // lowest unaligned or under consideration

        if (toAlign.elements[t].size() > 0) {
            return ((AElement)(toAlign.elements[t].get(0))).elementNumber;
        } else if (unaligned.elements[t].size() > 0) {
            return ((AElement)(unaligned.elements[t].get(0))).elementNumber;
        } else {
            return nodes[t].getLength() - 1;
        }
    }
}
