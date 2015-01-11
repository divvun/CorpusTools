package aksis.alignment;

/**
 * single word reference in a Cluster in Clusters.
 * what about phrases ############
 */
class Ref {

	// a reference to word pos in the considered elements of text t

	// type of match.
	// if the value is non-negative the match is an anchor word match,
	// and the value is the number of the matching entry in the anchor word list.
	// if the value is negative the match is some other match -
	// proper name match, Dice match, etc, depending on the value
	// (Match.PROPER, Match.DICE, etc)
	private int matchType;   // 2006-04-05
	// weight
	private float weight;   // 2006-04-05
	// text number
	private int t;
	// number of the element where the word occurs
	private int elementNumber;   // 2006-04-05
	//// word number (position) within the relevant elements of that text
	// the word's position within its element   // 2006-04-05
	// if it's a phrase: the position of the _first_ word in the phrase   // 2006-04-07
	private int pos;   // 2006-04-07
	// length of phrase   // 2006-04-07
	private int len;
	// word as written in the text.
	// if it's a phrase: words separated with space   // 2006-04-07
	private String word;

	Ref(int matchType, float weight, int t, int elementNumber, int pos, int len, String word) {   // 2006-04-07
		this.matchType = matchType;   // 2006-04-05
		this.weight = weight;   // 2006-04-05
		this.t = t;
		this.elementNumber = elementNumber;   // 2006-04-05
		this.pos = pos;
		this.len = len;   // 2006-04-07
		this.word = word;
	}

	// checks if equal content ### øh

	boolean matches(Ref otherRef) {
		//2006-04-05 // (not necessary to check match type or word)
		if ((this.t == otherRef.t) && (this.elementNumber == otherRef.elementNumber) && (Utils.overlaps(this.pos, this.len, otherRef.pos, otherRef.len))) {   // 2006-04-07
			// exactly the same word occurrence.
			// if phrase(s): at least one of the words in the phrases is exactly the same word occurrence.   // 2006-04-07
			// (this is the first possible kind of match)
			return true;
		} else {
			if (otherRef.matchType >= 0) {
				// the other ref is an anchor word ref
				if (this.matchType == otherRef.matchType) {
					// both are anchor words that belong to the same anchor word list entry.
					// (this is the second and last possible kind of match)
					return true;
				}
			}
		}

		return false;
		// end 2006-04-06
	}

	// 2006-04-06

	// vet ikke om bruk for denne
	boolean exactlyMatches(Ref otherRef) {
		// ####hva med weight?
		return ((this.matchType == otherRef.matchType) && (this.t == otherRef.t) && (this.elementNumber == otherRef.elementNumber) && (this.pos == otherRef.pos) && (this.len == otherRef.len));   // 2006-04-07
	}

	// 2006-04-05


	String getWord() {
		return word;
	}

	int getT() {
		return t;
	}

	int getMatchType() {
		return matchType;
	}

	// end 2006-04-05

	// for debugging or testing purposes.
	// the number of refs in the cluster
	public boolean typeAnchorWord() {
		return (matchType >= 0);
	}

	int getPos() {
		return pos;
	}

	// 2006-04-07
	float getWeight() {
		return weight;
	}

	boolean isInText(int t) {
		return (this.t == t);
	}

	// for debugging purposes

	public String toString() {
		return "[" + "matchType=" + matchType + ";weight=" + weight + ";t=" + t + ";elementNumber=" + elementNumber + ";pos=" + pos + ";len=" + len + ";word=" + word + "]";   // 2006-04-05
	}

}
