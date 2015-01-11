package aksis.alignment;

import javax.swing.DefaultListModel;

import java.util.Enumeration;
import java.util.List;
import java.util.Iterator;

/**
 * information about how the current elements under alignment match
 * with respect to anchor words, proper names, dice, length, etc.
 * displayable version.
 * formatted into a list of lines
 * ######### to ulike steder som beregner skåre
 */
class MatchInfo {

	AlignmentModel model;
	protected DefaultListModel displayableList;

	//MatchInfoDisplayable(AlignmentModel model) {
	MatchInfo(AlignmentModel model) {

		this.model = model;
		displayableList = new DefaultListModel();

	}

	public void clear() {   // §§§§§§§§§§§§§§§§§§§§§§§

		//...;

	}

	public void purge() {
		displayableList.clear();
		// (keep model)
	}

	//public String toString() {
	public void computeDisplayableList() {

		int t;
		int n;

		//System.out.println("computeDisplayableList()");

		ElementInfoToBeCompared elementInfoToBeCompared = new ElementInfoToBeCompared(model);

		// collect necessary info in an ElementInfoToBeCompared object

		for (t=0; t<Alignment.NUM_FILES; t++) {
			for (Enumeration en = model.toAlign.elements[t].elements(); en.hasMoreElements();) {
				n = ((AElement)en.nextElement()).elementNumber;
				try {
					ElementInfo info = model.compare.elementsInfo[t].getElementInfo(model, n, t);
					elementInfoToBeCompared.add(info, t);
				} catch (EndOfTextException e) {   // skal ikke forekomme her?
					System.out.println("*** program error.unexpected EndOfTextException ***");
					//return "*** program error. unexpected EndOfTextException ***";
					displayableList.add(0, (Object)"*** Program error. Unexpected EndOfTextException ***");
				}
			}
		}

		// get displayable info about how they match

		//return elementInfoToBeCompared.toString();
		List list = elementInfoToBeCompared.toList();
		Iterator it = list.iterator();
		displayableList.clear();
		while (it.hasNext()) {
			displayableList.addElement(it.next());
		}

	}

}

