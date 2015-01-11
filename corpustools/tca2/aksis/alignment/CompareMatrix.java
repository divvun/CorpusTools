package aksis.alignment;

import java.awt.Toolkit;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;
import java.util.Iterator;

/**
 * a matrix of CompareCells cells.
 * a cell represents the comparison of elements from the various texts.
 * there can be more then one element for each text, e.g, a 2-1 comparison.
 * so the matrix is not just a 2-dimensional array.
 * implemented as a Map,
 * with cells not calculated until they are needed,
 * and with garbage collection.
 * belongs to a Compare object
 */
class CompareMatrix {

	//...
	Map cells = new HashMap();   // map of CompareCells objects
	//Map cells = Collections.synchronizedMap(new HashMap());
	Map bestPathScores = new HashMap();   // map of BestPathScore objects

	public CompareMatrix() {
	}

	public void purge() {
		cells.clear();
		bestPathScores.clear();
	}

	void garbageCollect(int[] ix) {

		//System.out.println("CompareMatrix sin garbageCollect()");
		int currIx;
		Iterator it;
		String[] temp;
		String key;
		List keysToRemove;

		// ...

		it = cells.keySet().iterator();
		keysToRemove = new ArrayList();

		while (it.hasNext()) {
			//System.out.println("CompareMatrix sin garbageCollect(). neste cells");
			key = (String)it.next();
			//System.out.println("CompareMatrix sin garbageCollect(). key = " + key);
			temp = key.split(",");
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				currIx = Integer.parseInt(temp[t]);
				//System.out.println("CompareMatrix sin garbageCollect(). t = " + t + ". currIx = " + currIx);
				if (currIx < ix[t]) {
					// reclaim
					//String bestPathScoreKey = ((CompareCells)cells.get(key)).bestPathScoreKey;
					//System.out.println("CompareMatrix sin garbageCollect(). cells.remove(key)");
					//cells.remove(key);   // ¤¤¤ kommer til å gi exception? får i tilfelle samle opp nøklene og slette etter at iterasjonen har gått ferdig. - ja
					keysToRemove.add(key);
					//if (bestPathScores.containsKey(bestPathScoreKey)) {
					//	bestPathScores.remove(bestPathScoreKey);
					//}
					break;
				}
			}
		}

		it = keysToRemove.iterator();
		while (it.hasNext()) {
			key = (String)it.next();
			cells.remove(key);
		}

		// ...

		it = bestPathScores.keySet().iterator();
		keysToRemove = new ArrayList();

		while (it.hasNext()) {
			//System.out.println("CompareMatrix sin garbageCollect(). neste bestPathScores");
			key = (String)it.next();
			temp = key.split(",");
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				currIx = Integer.parseInt(temp[t]);
				//if (currIx < ix[t]) {
				if (currIx < ix[t] - 1) {   // ### 2005-11-03. seems we need a strip of cells above/left of the current area
					// reclaim
					//bestPathScores.remove(key);   // ¤¤¤ kommer til å gi exception? får i tilfelle samle opp nøklene og slette etter at iterasjonen har gått ferdig. - ja
					// #### i.g.n.m. det er mulig å ta it.remove() på aktuelle element i collection, og slippe keysToRemove-opplegget
					keysToRemove.add(key);
					break;
				}
			}
		}

		it = keysToRemove.iterator();
		while (it.hasNext()) {
			key = (String)it.next();
			///////////cells.remove(key); ############ 2005-11-01
			bestPathScores.remove(key);
		}

	}

	//float getScore(AlignmentModel model, int[] position) throws MyException {
	float getScore(AlignmentModel model, int[] position) {

		// can get the score from any cell ending in the position.
		// it doesn't matter which one.
		// if there are such cells (certainly there must be!!!???)
		// one of them must be a 1-1 cell. §§§§§§§§§§§§§§§§§
		// get it from that cell
		/*
		String key11 = "";
		// ¤¤¤ heller lage en String join-metode? eller bruke int array som nøkkel i stedet for streng?
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			if (t>0) { key11 += ","; }
			key11 += Integer.toString(position[t]);
		}
		key11 = key11 + "," + key11;
		//System.out.println("CompareMatrix sin getScore(). key11=" + key11);
		*/
		boolean outside = false;
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			if (position[t] < 0) {
				outside = true;
				break;
			}
		}
		if (outside) {
			//return (float)0.0;
			//System.out.println("outside");
			//return -1.0f;   // a value less than real scores. smallest possible real score is 0
			return AlignmentModel.BEST_PATH_SCORE_BAD;   // 2006-09-20
		} else {
			// ...
			String bestPathScoreKey = "";
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				if (t>0) { bestPathScoreKey += ","; }
				bestPathScoreKey += position[t];
			}
			//System.out.println("getScore() kalt for key=" + bestPathScoreKey);
			//
			if (bestPathScores.get(bestPathScoreKey) == null) {
				/*
				// ###cell does not exist. %¤#%¤#%¤#%¤#create cell
				//System.out.println("cell does not exist. create cell. key=" + key);
				CompareCells compareCells = model.compare.getCellValues(model, position[0], position[1]);
				return compareCells.bestPathScore;
				*/
				//throw new MyException("Noe gikk feil!!!!");   // §§§§§§§§§§§§§§§§§§§§§§§
				Toolkit.getDefaultToolkit().beep();   // §§§§§§§§§§§§§§§§§§§§§§§
				Toolkit.getDefaultToolkit().beep();   // §§§§§§§§§§§§§§§§§§§§§§§
				Toolkit.getDefaultToolkit().beep();   // §§§§§§§§§§§§§§§§§§§§§§§
				Toolkit.getDefaultToolkit().beep();   // §§§§§§§§§§§§§§§§§§§§§§§
				Toolkit.getDefaultToolkit().beep();   // §§§§§§§§§§§§§§§§§§§§§§§
				//System.out.println("cell doesn't exist. BEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEP CompareMatrix getScore");
				System.out.println("Program error? Cell doesn't exist. Position = " + position[0] + "," + position[1]);
				//return 0;   // §§§§§§§§§§§§§§§§§§§§§§§
				//return -1.0f;   // a value less than real scores. smallest possible real score is 0. 2005-08-22
				return AlignmentModel.BEST_PATH_SCORE_BAD;   // 2006-09-20
			} else {
				//System.out.println("cell exists. bestPathScoreKey=" + bestPathScoreKey);
				//System.out.println("skåre = " + ((BestPathScore)bestPathScores.get(bestPathScoreKey)).getScore());
				return ((BestPathScore)bestPathScores.get(bestPathScoreKey)).getScore();
			}
		}
	}

	void setScore(int[] position, float score) {
		String bestPathScoreKey = "";
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			if (t>0) { bestPathScoreKey += ","; }
			bestPathScoreKey += Integer.toString(position[t]);
		}
		//System.out.println("setScore() setter best path score=" + score + " for key=" + bestPathScoreKey);
		bestPathScores.put(bestPathScoreKey, new BestPathScore(score));
		/*
		// must set score in all cells ending in this position. ### neida. alle relevante celler peker jo hit med sin bestPathScore
		// §§§§§§§§§§§§§§§§§§§§§§§§§§§ dårlig programmering
		String keyEnd = "," + bestPathScoreKey;
		Iterator it = cells.keySet().iterator();
		while (it.hasNext()) {
			String key = (String)it.next();
			if (key.substring(key.length() - keyEnd.length(), key.length()).equals(keyEnd)) {
				// match
				((CompareCells)(cells.get(key))).bestPathScoreKey = bestPathScoreKey;
			}
		}
		*/
		//System.out.println("setScore() setter member bestPathScore. score=" + score + ", key=" + key);
		return;
	}

	void resetBestPathScores() {
		Iterator it = bestPathScores.keySet().iterator();
		while (it.hasNext()) {
			//bestPathScores.put(it.next(), new BestPathScore(-1.0f));   // ##### burde hatt konstanter for disse to stedene hvor jeg bruker (float)-1? bruker det både for cells-greie og best path
			bestPathScores.put(it.next(), new BestPathScore(AlignmentModel.BEST_PATH_SCORE_NOT_CALCULATED));   // 2006-09-20
		}
	}

	// §§§ for debugging

	public String toString() {
		String ret = "";
		String key;
		Iterator it1 = cells.keySet().iterator();
		while (it1.hasNext()) {
			key = (String)it1.next();
			//System.out.println("cells. key=" + key);
			ret += "(" + key + " : ";
			ret += (CompareCells)cells.get(key);
			ret += ")\n";
		}
		Iterator it2 = bestPathScores.keySet().iterator();
		while (it2.hasNext()) {
			key = (String)it2.next();
			//System.out.println("bestPathScores. key=" + key);
			ret += "(" + key + " : ";
			ret += (BestPathScore)bestPathScores.get(key);
			ret += ")\n";
		}
		return ret;
	}

}

