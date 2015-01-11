package aksis.alignment;

import java.util.List;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Collections;



/**
 * single cluster in Clusters.
 * list of all word references belonging to the cluster.
 * 2006-04-06
 * a cluster collects word occurrences that are related.
 * e.g, two words from _either_ text, matching the same anchor word entry, are related.
 * e.g, two words from the _same_ text, matching the same anchor word entry, are related.
 * the first case is a real case of matching words,
 * the other one not.
 * the calling methods are responsible for not adding references that do not represent matches
 */
class Cluster implements Cloneable {

	List<Ref> refs;   // list of Ref
	
	Cluster() {   // 2006-04-05
		refs = new ArrayList<Ref>();
	}

    public Object clone() {
        try {
            return super.clone();
        } catch (CloneNotSupportedException e) {
            throw new Error("This should not occur since we implement Cloneable");
        }
    }

	List<Ref> getRefs() {   // 2006-04-05
		return refs;
	}

	void add(Ref otherRef) {
		Iterator<Ref> rIt = refs.iterator();
		Ref ref;
		while (rIt.hasNext()) {
			ref = rIt.next();
			if (ref.exactlyMatches(otherRef)) {   // 2006-04-06 vet ikke om det noensinne vil bli eksakt match
				// the cluster already contains this reference
				// (necessarily with the same word)
				return;
			}
		}
		// this reference is new.
		// add it to the cluster
		refs.add(otherRef);

        return;
	}

	boolean matches(Ref otherRef) {
		// does this cluster match other ref?
		Iterator<Ref> rIt = refs.iterator();
		Ref ref;
		while (rIt.hasNext()) {
			ref = rIt.next();
			if (ref.matches(otherRef)) {
				return true;
			}
		}

		return false;
	}

	boolean matches(Cluster otherCluster) {
		Iterator<Ref> orIt = otherCluster.refs.iterator();
		Ref otherRef;
		while (orIt.hasNext()) {
			otherRef = orIt.next();
			if (this.matches(otherRef)) {
				return true;
			}
		}
		
		return false;
	}

	void add(Cluster otherCluster) {
		Iterator<Ref> orIt = otherCluster.refs.iterator();
		Ref otherRef;
		while (orIt.hasNext()) {
			otherRef = orIt.next();
			this.add(otherRef);
		}
	}

	// a cluster contains references to words in several text (in practice two texts).
	// some texts may have more references than others,
	// and this method finds the largest number of references
	float getScore(int largeClusterScorePercentage) {
		int high = 0;
		int low = Integer.MAX_VALUE;
		Iterator<Ref> rIt;
		Ref ref;
		float clusterWeight = 0.0f;   // 2006-04-07
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			int count = 0;
			List<Integer> positions = new ArrayList<Integer>();   // list to collect unique positions
			rIt = refs.iterator();
			while (rIt.hasNext()) {
				ref = rIt.next();
				if (ref.isInText(t)) {
					if (!positions.contains(ref.getPos())) {
						positions.add(ref.getPos());
					}
					clusterWeight = Math.max(clusterWeight, ref.getWeight());   // 2006-04-07
				}
				count = positions.size();
			}

			low = Math.min(low, count);
			high = Math.max(high, count);
		}

		return clusterWeight * ( 1 + ((low - 1) * largeClusterScorePercentage / 100.0f) );
	}

	List<String> getWords(boolean includeMatchType) {   // List of String   // 2006-04-05
		// includeMatchType ### ugly ### + 1
		// 2006-04-05
		// må kunne returnere en hel liste av String,
		// for det kan være flere matchType-r i clusteret,
		// i praksis match-er for mer enn én ankerordsentry
		Cluster sortedCluster = (Cluster)this.clone();
		// sort on (1) match type (in case it contains anchor word entry number), (2) text number, (3) word   // 2006-04-05
		Collections.sort(sortedCluster.refs, new RefComparator());
		Iterator<Ref> rIt = sortedCluster.refs.iterator();
		List<String> ret = new ArrayList<String>();   // the list to return   // 2006-04-05
		String retLine = "";   // one item in the list
		int prevMatchType = Integer.MIN_VALUE;   // 2006-04-05
		int prevT = -1;
		int numSlashes;
		boolean firstInCurrMatchType;   // 2006-04-05
		boolean firstInCurrText;
		while (rIt.hasNext()) {
			Ref ref = rIt.next();
			firstInCurrMatchType = (ref.getMatchType() > prevMatchType);
			if (firstInCurrMatchType) {
				// starting on a new match type,
				// i.e, starting on a new item in the list to return
				// add the current item - if any - to the list before starting anew
				if (retLine != "") {
					ret.add(retLine);
					// reset
					retLine = "";
					prevT = -1;
				}

				if (includeMatchType) {
					// ### ugly ###
					int matchType = ref.getMatchType();
					int temp = matchType + 1;   // ### +1 because we want human numbering of anchor word entries
					                            // ugly because in principle there could be a value for something different than the number of a anchor word entry
					retLine += temp + " ";
				}
			}

			firstInCurrText = (ref.getT() > prevT);   // 2006-04-05

            if (firstInCurrText) {
				if (firstInCurrMatchType) {   // 2006-04-05
					numSlashes = ref.getT() - prevT -1;   // 2006-04-05
					firstInCurrMatchType = false;   // 2006-04-05
				} else {
					numSlashes = ref.getT() - prevT;   // 2006-04-05
				}
				for (int i=0; i<numSlashes; i++) { retLine += "/"; };
			} else {
				retLine += ",";
			}
			retLine += ref.getWord();   // 2006-04-05
			prevT = ref.getT();   // 2006-04-05
			prevMatchType = ref.getMatchType();   // 2006-04-06
		}
		// 2006-04-06
		if (retLine != "") {
			ret.add(retLine);
		}

		return ret;   // 2006-04-05

	}

	// for debugging or testing purposes.
	// the number of refs in the cluster
	public int size() {
		return getRefs().size();
	}

	// for debugging or testing purposes.
	// the number of anchor word refs in the cluster
	public int countAnchordWordRefs() {
		int count = 0;
		Ref ref;
		Iterator<Ref> rIt = getRefs().iterator();
		while (rIt.hasNext()) {
			ref = rIt.next();
			if (ref.typeAnchorWord()) {
				count++;
			}
		}
		return count;
	}

	// for debugging or testing purposes.
	// the number of anchor word entries for the cluster
	public int countAnchordWordEntries() {
		List<Integer> anchorWordEntryNumbers = new ArrayList<Integer>();
		Ref ref;
		Iterator<Ref> rIt = getRefs().iterator();
		while (rIt.hasNext()) {
			ref = rIt.next();
			if (ref.typeAnchorWord() && !anchorWordEntryNumbers.contains(ref.getMatchType())) {
				anchorWordEntryNumbers.add(ref.getMatchType());
			}
		}
		return anchorWordEntryNumbers.size();
	}

	// for debugging purposes
	public String toString() {
		//Iterator rIt = refs.iterator();
		Iterator<Ref> rIt = getRefs().iterator();
		Ref ref;
		String retVal = "";
		boolean first = true;
		retVal += "(";
		while (rIt.hasNext()) {
			ref = rIt.next();
			if (first) {
				first = false;
			} else {
				retVal += ",";
			}
			retVal += ref.toString();
		}
		retVal += ")";
		return retVal;
	}

	// for debugging or testing purposes.
	// makes string representation of cluster
	// if the cluster is "non-trivial",
	// i.e, more than one anchor word entry is involved
	public String nonTrivialCluster_ToString() {
		String retVal = "";

        if (countAnchordWordEntries() > 2) {
			Iterator<Ref> rIt = getRefs().iterator();
			Ref ref;
			boolean first = true;
			while (rIt.hasNext()) {
				ref = rIt.next();
				if (first) {
					first = false;
				} else {
					retVal += "\n";
				}
				retVal += ref.toString();
			}
			retVal += "\n";
		}
		if (retVal != "") {
			retVal = "non-trivial cluster:\n\n" + retVal;
		}
		return retVal;
	}

}
