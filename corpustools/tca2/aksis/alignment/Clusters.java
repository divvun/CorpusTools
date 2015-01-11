/*
 * Clusters.java
 *
 * ... a place to collect all necessary information
 * about matches for the elements under consideration,
 * be they
 * anchor word matches,
 * proper names matches,
 * dice matches,
 * all of the three, i.e, all the word based methods,
 * or special character matches
 * ...
 * @author Oystein Reigem
 */

package aksis.alignment;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/**
 * information about how related words in the texts collect in clusters
 */
class Clusters {

	List<Cluster> clusters;   // list of Cluster

	Clusters() {   // 2006-04-05
		clusters = new ArrayList<Cluster>();
	}

	// word pos1 in element elementNumber1 in text t (word1) is related to
	// word pos2 in element elementNumber2 in text tt (word2).
	// matchType is the type of match, as explained elsewhere.
	// weight is the weight assigned to the match.
	// add that information
	void add(int matchType, float weight, int t, int tt, int elementNumber1, int elementNumber2, int pos1, int pos2, int len1, int len2, String word1, String word2) {   // 2006-04-05

		// make a new Cluster from the new word references.
		// add the new Cluster.
		// important that the two Ref's are added as a Cluster and not as single Ref's,
		// because the Ref.add(Ref) method would not be able to cluster them,
		// because the ref.matches(Ref) method would not recognize them as related

		Cluster newCluster = new Cluster();

        newCluster.add(new Ref(matchType, weight, t,  elementNumber1, pos1, len1, word1));   // 2006-04-07
		newCluster.add(new Ref(matchType, weight, tt, elementNumber2, pos2, len2, word2));   // 2006-04-07
		add(newCluster);
	}   // 2006-04-05

	void add(Ref ref) {   // 2006-04-05

		//// make a new cluster from the new word reference   // 2006-04-05

		List<Cluster> overlaps = new ArrayList<Cluster>();   // list of Cluster

		Iterator<Cluster> cIt = clusters.iterator();
		Cluster cluster;
		while (cIt.hasNext()) {
			cluster = (Cluster)cIt.next();
			if (cluster.matches(ref)) {
				overlaps.add(cluster);
			}
		}

		//// merge the new cluster with all overlapping clusters
		// merge the ref with all overlapping clusters.
		// first make a cluster from the ref
		Cluster mergedCluster = new Cluster();   // 2006-04-05
		mergedCluster.add(ref);   // 2006-04-05

		Iterator<Cluster> oIt = overlaps.iterator();
		while (oIt.hasNext()) {
			cluster = (Cluster)oIt.next();
			mergedCluster.add(cluster);
			clusters.remove(cluster);
		}

		// add the new, merged cluster
		clusters.add(mergedCluster);

	}

	// merge two Clusters
	void add(Clusters otherClusters) {
		Iterator<Cluster> ocIt = otherClusters.clusters.iterator();
		while (ocIt.hasNext()) {
			Cluster otherCluster = (Cluster)ocIt.next();
			add(otherCluster);
		}
	}

	// add a Cluster to a Clusters
	void add(Cluster otherCluster) {
		List<Cluster> overlaps = new ArrayList<Cluster>();   // list of Cluster

		Iterator<Cluster> cIt = clusters.iterator();
		Cluster cluster;
		while (cIt.hasNext()) {
			cluster = (Cluster)cIt.next();
			Iterator<Ref> orIt = otherCluster.refs.iterator();
			boolean match = false;
			while (orIt.hasNext()) {
				Ref otherRef = (Ref)orIt.next();
				if (cluster.matches(otherRef)) {
					match = true;
					break;
				}
			}
			if (match) {
				// one ref in the other cluser matched, and therefore the whole cluster matched
				overlaps.add(cluster);
			}
		}

		// clone the other cluster and merge it with all overlapping clusters
		Cluster mergedCluster = (Cluster)otherCluster.clone();

		Iterator<Cluster> oIt = overlaps.iterator();
		while (oIt.hasNext()) {
			cluster = (Cluster)oIt.next();
			mergedCluster.add(cluster);
			clusters.remove(cluster);
		}

		// add the new, merged cluster
		clusters.add(mergedCluster);
	}

	float getScore(int clusterScoreMethod) {   // 2006-04-07
		float score = 0.0f;   // 2006-04-07

		// each cluster adds to the score.
		// each cluster contains references to words in several text (in practice 2).
		// the score is the largest number of referred words in any text
		Iterator<Cluster> cIt = clusters.iterator();
		Cluster cluster;
		while (cIt.hasNext()) {
			cluster = (Cluster)cIt.next();
			score += cluster.getScore(clusterScoreMethod);
		}

		return score;

	}

	List getDetails(int indentLevel, boolean includeMatchType) {   // 2006-04-05
		Iterator<Cluster> cIt = clusters.iterator();
		Cluster cluster;
		List<String> ret = new ArrayList<String>();

        while (cIt.hasNext()) {
			cluster = (Cluster)cIt.next();
			String indentation = "";
			for (int i = 0; i < indentLevel; i++) { indentation += ElementInfoToBeCompared.INDENT; }   // ¤¤¤¤¤¤¤¤¤¤ ElementInfoToBeCompared ¤¤¤ INDENT
			List<String> lines = cluster.getWords(includeMatchType);
			for (int j = 0; j < lines.size(); j++) {
				ret.add(indentation + lines.get(j));
			}
		}

		return ret;

	}

	// for debugging purposes
	public String toString() {
		Iterator<Cluster> cIt = clusters.iterator();
		Cluster cluster;
		String retVal = "";
		boolean first = true;
		retVal += "{ ";
		while (cIt.hasNext()) {
			cluster = (Cluster)cIt.next();
			if (first) {
				first = false;
			} else {
				retVal += " ; ";
			}
			retVal += cluster.toString();
		}
		retVal += " }";
		return retVal;
	}

	// for debugging or testing purposes
	public String nonTrivialClusters_ToString() {
		Iterator<Cluster> cIt = clusters.iterator();
		Cluster cluster;
		String retVal = "";
		String temp;
		boolean first = true;
		while (cIt.hasNext()) {
			cluster = (Cluster)cIt.next();
			temp = cluster.nonTrivialCluster_ToString();
			if (temp != "") {
				if (first) {
					first = false;
				} else {
					retVal += "\n";
				}
				retVal += temp;
			}
		}
		if (retVal != "") {
			retVal = "(This is not an error message)\nCONTAINS NON-TRIVIAL CLUSTERS:\n\n" + retVal;
		}
		return retVal;
	}

}




