package aksis.alignment;

import java.util.TreeSet;
import java.util.Iterator;

/**
 * each Link object represents an alignment - a finished one or pending one.
 * ##########################################################in addition a Link object is used for unused elements under consideration.
 */
class Link {

	/**
	 * alignments are numbered 0, 1, 2, 3, ...
	 * the numbering is global, so the numbering of pending alignments
	 * continues the numbering of finished alignments.
	 * #################################################unused elements under consideration have a special number -1. ¤¤¤UNUSED
	 */
	int alignmentNumber;   // ########################skulle hatt set-metode. m.fl.

	/**
	 * the numbers of the elements involved in the alignment.
	 * one set for each text.
	 */
	TreeSet[] elementNumbers;

	Link() {
		alignmentNumber = -1;   // ¤¤¤
		elementNumbers = new TreeSet[Alignment.NUM_FILES];
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			//elementNumbers[t] = new TreeSet();   // TreeSet is a SortedSet
			elementNumbers[t] = new TreeSet<Integer>();   // TreeSet is a SortedSet   // 2006-11-20
		}
	}

	TreeSet getElementNumbers(int t) {
		return elementNumbers[t];
	}

	boolean empty() {
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			if (elementNumbers[t].size() > 0) {
				return false;
			}
		}
		return true;
	}

	int countElements() {
		int count = 0;
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			count += elementNumbers[t].size();
		}
		return count;
	}

	public String toString() {
		String str = "(";
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			if (t > 0) { str += ";"; }
			str += "size=" + elementNumbers[t].size();
			Iterator e = ((TreeSet)(elementNumbers[t])).iterator();
			while (e.hasNext()) {
				str += ",el=";
				str += e.next();
			}
		}
		str += ")";
		str += " alignment nummer " + alignmentNumber;
		return str;
	}

}

