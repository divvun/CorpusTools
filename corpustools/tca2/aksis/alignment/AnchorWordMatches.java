/*
 * AnchorWordMatches.java
 *
 * ...
 * ...
 * @author Oystein Reigem
 */

package aksis.alignment;

import java.util.Iterator;
import java.util.ArrayList;

/**
 * information about all the anchor word matches
 * for the elements under alignment -
 * a list of all the single matches
 */
class AnchorWordMatches {

	java.util.List<AnchorWordMatch> matches;

	AnchorWordMatches() {

		matches = new ArrayList<AnchorWordMatch>();

	}

	public void add(AnchorWordMatch match) {

		matches.add(match);

	}

	// ### for debugging (?)
	public String toString() {

		Iterator<AnchorWordMatch> it = matches.iterator();
		StringBuffer ret = new StringBuffer();
		ret.append("[");
		while (it.hasNext()) {
			ret.append(",");
			ret.append(((AnchorWordMatch)it.next()).toString());
		}
		ret.append("]");

		return new String(ret);

	}

}
