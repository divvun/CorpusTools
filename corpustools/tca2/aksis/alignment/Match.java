/*
 * Match.java
 *
 * ...
 * ...
 * @author Oystein Reigem
 */

package aksis.alignment;

// ### just needed a place to put some constants
// that have to do with finding matches between elements under consideration.

class Match {

	// various types of match between words etc

	// for anchor word matches the number of the anchor word entry is used
	public static int PROPER = -1;   // the match is a proper name match
	public static int DICE = -2;   // the match is a dice match
	public static int NUMBER = -3;   // the match is a number match
	public static int SCORING_CHARACTERS = -11;   // the match is a special character match
	// (values must be larger than Integer.MIN_VALUE)

}


