package aksis.alignment;

/**
 * scores from comparing elements from different texts,
 * either ...
 * or ... .
 * ### CompareCells dårlig navn. cell dårlig navn. eller??
 * belongs to a CompareMatrix object
 */
class CompareCells {

	ElementInfoToBeCompared elementInfoToBeCompared;

	// textual representation of match info
	String matchInfoDisplayable;
	BestPathScore bestPathScore;

	// ### new version 2005-06-30 for comparison of ###steps and not just single cells.
	public CompareCells(AlignmentModel model, int[] position, PathStep step) throws EndOfAllTextsException, EndOfTextException {

 		//System.out.println("CompareCells constructor. position=" + position[0] + "," + position[1] + " , step=" + step);

		//bestPathScore = new BestPathScore();

		elementInfoToBeCompared = new ElementInfoToBeCompared(model);

		// loop through all texts and collect info for comparison

		int textEndCount = 0;
		for (int t=0; t<Alignment.NUM_FILES; t++) {

			// loop through all relevant elements of the current text

			for (int x = position[t] + 1; x <= position[t] + step.increment[t]; x++) {

				// get element info
				try {
					ElementInfo info = model.compare.elementsInfo[t].getElementInfo(model, x, t);
					elementInfoToBeCompared.add(info, t);
				} catch (EndOfTextException e) {
					//System.out.println("CompareCells constructor. end of text " + t);
					textEndCount++;
					//throw e;   // ¤¤¤ er dette måten ...?
					break;
				}
				// add to "collection"

			}

		}

		//
		//if (textEndCount > 0) {
		//	System.out.println("CompareCells constructor. textEndCount = " + textEndCount);
		//}
		if (textEndCount >= Alignment.NUM_FILES) {
			//System.out.println("CompareCells constructor throws EndOfAllTextsException");
			throw new EndOfAllTextsException();
		} else if (textEndCount > 0) {
			//System.out.println("CompareCells constructor throws EndOfTextException");
			throw new EndOfTextException();
		}

		// actual comparison done later
		// ### no - done now

		//System.out.println("CompareCells constructor. på slutten. kaller elementInfoToBeCompared.getScore()");
		elementInfoToBeCompared.getScore();
 		//System.out.println("CompareCells constructor. på slutten. etter kall av elementInfoToBeCompared.getScore()");

	}

	//public int getScore() {
	public float getScore() {

		return elementInfoToBeCompared.getScore();

	}

	// §§§ for debugging
	public String toString() {
		//
		//System.out.println("CompareCells' toString");
		////return "CompareCells' toString. score=" + score + ", best path score=" + bestPathScore.getScore();
		return "CompareCells' toString. score=" + elementInfoToBeCompared.getScore() + ", best path score=" + bestPathScore.getScore();
	}

}

