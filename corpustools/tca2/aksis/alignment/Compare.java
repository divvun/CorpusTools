/*
 * Compare.java
 *
 * ...
 * ...
 * @author Oystein Reigem
 */

package aksis.alignment;

import java.awt.Color;
import java.util.*;
import java.io.*;
import java.util.regex.*;
import javax.swing.*;
import java.awt.event.MouseEvent;
import java.lang.reflect.*;
import java.awt.Toolkit;   // beep
//java.util.regex.Pattern

/////////////////////////////////////////////
// the world of the alignment algorithm(s) //
/////////////////////////////////////////////


/**
 * ...
 */
class Compare {

	// info about elements in each text
	ElementsInfo[] elementsInfo = new ElementsInfo[Alignment.NUM_FILES];
	// info about how elements combine
	CompareMatrix matrix = new CompareMatrix();

	// list of the various possible steps (e.g, 1-1, 0-1, 1-0, 1-2, etc)
	List stepList = new ArrayList();

	Compare() {
		//System.out.println("Compare constructor");
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			elementsInfo[t] = new ElementsInfo();
		}
		createStepList();
	}
	public void purge() {
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			elementsInfo[t].purge();
		}
		matrix.purge();
		createStepList();
	}


	// ### new version 2005-06-30 for comparison of ###steps and not just single cells
	// ### CompareCells getCellValues not good names
	public CompareCells getCellValues(AlignmentModel model, int[] position, PathStep step) throws EndOfAllTextsException, EndOfTextException {

		// ### position er vel siste pos i sti så langt (XXX)
		// da starter den nye cellen etter denne pos:
		//
		// XXX
		//     her
		String key = "";
		String bestPathScoreKey = "";
		// cell start position
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			if (t>0) { key += ","; }
			key += Integer.toString(position[t] + 1);
		}
		// ...
		key += ",";
		// cell end position
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			if (t>0) {
				key += ",";
				bestPathScoreKey += ",";
			}
			key += Integer.toString(position[t] + 1 + step.increment[t] - 1);
			bestPathScoreKey += Integer.toString(position[t] + 1 + step.increment[t] - 1);
		}
		//int x, y, xInc, yInc;
		//x = position[0];
		//System.out.println("getCellValues method new version");
		//// key format: start x , start y , end x , end y
		//String key = Integer.toString(x) + "," + Integer.toString(y) + "," + Integer.toString(x+xInc-1) + "," + Integer.toString(y+yInc-1);
		//System.out.println("getCellValues. key = " + key);

		if (!matrix.cells.containsKey(key)) {
				//System.out.println("!matrix.cells.containsKey(key)");
				// make a new cells thing ###
				// ### with a bestPathScore reference not yet set
				try {
					matrix.cells.put(key, new CompareCells(model, position, step));
				} catch (EndOfAllTextsException e) {
					//System.out.println("getCellValues() throws EndOfAllTextsException");
					throw e;   // ¤¤¤ er dette måten ...?
				} catch (EndOfTextException e) {
					//System.out.println("getCellValues() throws EndOfTextException");
					throw e;   // ¤¤¤ er dette måten ...?
				}

				if (matrix.bestPathScores.containsKey(bestPathScoreKey)) {
					// there is a best score for this end position.
					// use it
					//((CompareCells)matrix.cells.get(key)).bestPathScore = (BestPathScore)matrix.bestPathScores.get(bestPathScoreKey);
					// (((this version just to see where the ClassCastException occurs)))
					BestPathScore temp = (BestPathScore)matrix.bestPathScores.get(bestPathScoreKey);
					((CompareCells)matrix.cells.get(key)).bestPathScore = temp;
				} else {
					// there is no best score for this end position.
					// set very low value ### no not that ### uh
					((CompareCells)matrix.cells.get(key)).bestPathScore = new BestPathScore();
				}

				// put the best score object in the best score map
				matrix.bestPathScores.put(bestPathScoreKey, ((CompareCells)matrix.cells.get(key)).bestPathScore);   // ####

				//System.out.println("satt inn ny celle. matrix er nå\n" + matrix);
			//}
		}
		return (CompareCells)matrix.cells.get(key);

	}

	void createStepList() {

		//
		//System.out.println("createStepList");
		int range = Alignment.MAX_NUM_TRY - Alignment.MIN_NUM_TRY + 1;
		int limit = 1;
		for (int j=0; j<Alignment.NUM_FILES; j++) {
			limit *= range;
		}
		//System.out.println("limit = " + limit);
		// a list of all the possible steps to make from a node/cell in a path.
		// each step is an array of increments along the file axes ¤¤¤
		int[] increment;
		for (int i = 0; i < limit; i++) {
			increment = new int[Alignment.NUM_FILES];
			//System.out.println("==>" + Integer.toString(limit + i, range));
			String combString = Integer.toString(limit + i, range).substring(1,Alignment.NUM_FILES+1);
			int minimum = Alignment.MAX_NUM_TRY + 1;
			int maximum = Alignment.MIN_NUM_TRY - 1;
			int total = 0;
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				//System.out.println("combString=" + combString);
				increment[t] = Alignment.MIN_NUM_TRY + Integer.parseInt(combString.substring(t,t+1), range);
				total += increment[t];
				minimum = Math.min(minimum, increment[t]);
				maximum = Math.max(maximum, increment[t]);
				//System.out.println("minimum=" + minimum);
				//System.out.println("maximum=" + maximum);
			}
			//System.out.println("final minimum=" + minimum);
			//System.out.println("final maximum=" + maximum);
			//if (maximum > 0 && maximum - minimum <= Alignment.MAX_DIFF_TRY) {
			if (maximum > 0 && maximum - minimum <= Alignment.MAX_DIFF_TRY && total <= Alignment.MAX_TOTAL_TRY) {
				// acceptable combination
				//System.out.println("*** ny increment er {" + increment[0] + ", " + increment[1] + "}");
				stepList.add(new PathStep(increment));
				//System.out.println("stepList.size() = " + stepList.size());
			}
		}

	}

	float getScore(AlignmentModel model, int[] position) {
		return matrix.getScore(model, position);
	}

	void setScore(int[] position, float score) {
		matrix.setScore(position, score);
		return;
	}

	// §§§ for debugging
	public String toString() {
		return "\n*************\nCompare sin matrix:\n" + this.matrix.toString() + "\n";
	}

/*
From here on: Functions that are used by suggestWithoutGui
*/

    /* delete everything before, but not including, int[] ix */
    void garbageCollect(AlignmentModel model, int[] ix) {
        //System.out.println("Compare sin garbageCollect(). før matrix.garbageCollect()");
        matrix.garbageCollect(ix);
        //System.out.println("Compare sin garbageCollect(). etter matrix.garbageCollect()");
        for (int t=0; t<Alignment.NUM_FILES; t++) {
            //System.out.println("Compare sin garbageCollect(). før elementsInfo[t].setFirst()");
            elementsInfo[t].setFirst(model, ix[t], t);
            ////elementsInfo[t].setFirst(model, ix[t], t, elementNumber);   // 2006-04-05
        }
    }

    void resetBestPathScores() {
        matrix.resetBestPathScores();
    }
}

