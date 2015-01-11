/*
 * AnchorWordHits.java
 *
 * ...
 * ...
 * ...
 */

package aksis.alignment;

import java.util.*;
import java.lang.String;

// ...

class AnchorWordHit {

	Integer index;   // refers to entry in anchor word list
	int elementNumber;   // element number   // 2006-04-05
	int pos;   // position of word within its element. 2006-04-04. 2006-04-05 or several elements! ###
	String word;   // word as written in the text

	public AnchorWordHit(Integer index, int elementNumber, int pos, String word) {   // 2006-04-04, 2006-04-05
		this.index = index;
		this.elementNumber = elementNumber;   // 2006-04-05
		this.pos = pos;   // 2006-04-04
		this.word = word;
	}

	public Integer getIndex() {
		return index;
	}

	public String getWord() {
		return word;
	}

	// 2006-04-04
	public int getPos() {
		return pos;
	}

	// 2006-04-05
	public Integer getElementNumber() {
		return elementNumber;
	}

	// 2006-04-05
	public void setPos(int pos) {
		this.pos = pos;
	}

	// ### for debugging
	public String toString() {
		return "(index=" + index.intValue() + ";pos=" + pos + ";word=" + word + ")";
	}

}

class AnchorWordHits {

	java.util.List<AnchorWordHit> hits;

	public AnchorWordHits () {
		hits = new ArrayList<AnchorWordHit>();
	}

	public void add(AnchorWordHit hit) {
		hits.add(hit);
	}

	// ### for debugging
	public String toString() {
		Iterator<AnchorWordHit> it = hits.iterator();
		StringBuffer ret = new StringBuffer();
		ret.append("[");
		while (it.hasNext()) {
			if (ret.equals("[")) { ret.append(","); }
			ret.append(it.next());
		}
		return new String(ret);
	}

}

