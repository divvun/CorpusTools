package aksis.alignment;

import javax.swing.DefaultListModel;
import java.awt.Toolkit;

import java.util.List;
import java.util.ArrayList;
import java.util.Set;
import java.util.TreeSet;


class Aligned {

	/**
	 * lists of aligned elements.
	 * one list for each text.
	 * shown in the gui's 'aligned' JList components.
	 * each element is an AElement object.
	 */
	protected DefaultListModel[] elements;

	/**
	 * the finished alignments.
	 * each alignment is a Link object.
	 */
	List<Link> alignments = new ArrayList<Link>();   // package access. list of Link objects. 2006-11-20

	Aligned() {
		elements = new DefaultListModel[Alignment.NUM_FILES];
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			elements[t] = new DefaultListModel();
		}
	}

	public void purge() {
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			elements[t].clear();
		}
		alignments.clear();
	}

	public boolean hasHoles(Set[] integerSet) {
		// check if the n latest finished alignments
		// (the n bottom alignments)
		// have any holes.
		// for each text see if there are holes
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			if (((TreeSet)(integerSet[t])).size() > 0) {
				// there are elements in this text covered by the n latest alignments.
				// find the number of the highest element aligned for this text.
				// note that there might be crossing alignments,
				// so this element might not be covered by the n latest ones
				int high = ((AElement)(elements[t].get(elements[t].size()-1))).elementNumber;
				// find the number of the lowest element covered by the n latest alignments
				int low = ((Integer)(((TreeSet)(integerSet[t])).last())).intValue();
				// is there a hole?
				if (((TreeSet)(integerSet[t])).size() < (high-low+1)) {
					// yes
					return true;
				}
			}
		}
		return false;
	}

	AlignmentsEtc drop(AlignGui gui) {
		// can't just go ahead and drop bottom alignment.
		// must make sure there are no holes due to crossing alignments.
		// scan alignments from bottom upwards until there are no holes.¤¤¤
		if (alignments.size() == 0) {
			Toolkit.getDefaultToolkit().beep();
			System.out.println("Nothing to drop");
			return null;
		} else {
			Set[] testElementNumbers = new TreeSet[Alignment.NUM_FILES];   // TreeSet is a sorted Set
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				Set<Integer> s = new TreeSet<Integer>();   // TreeSet is a sorted Set. 2006-11-20
				testElementNumbers[t] = s;
			}
			boolean holes = true;   // pessimistic ¤¤¤
			// find the first alignment to drop
			int numberOfFirstAlignmentToDrop = alignments.size() - 1;
			while (holes) {
				if (numberOfFirstAlignmentToDrop < 0) {
					ErrorMessage.programError("AlignmentsEtc drop(). numberOfFirstAlignmentToDrop < 0");   // 2006-08-10
					return null;
				}
				for (int t=0; t<Alignment.NUM_FILES; t++) {
					testElementNumbers[t].addAll(((Link)(alignments.get(numberOfFirstAlignmentToDrop))).getElementNumbers(t));
				}
				if (!hasHoles(testElementNumbers)) {   // ¤¤¤var ikke bra nok. høyeste element-nummer må også være med. ellers oppdages ikke kryssing likevel
					holes = false;
				} else {
					numberOfFirstAlignmentToDrop--;
				}
			}
			//
			AlignmentsEtc returnValue = new AlignmentsEtc();
			// elements belonging to alignments starting with number 'numberOfFirstAlignmentToDrop' are to be dropped
			//System.out.println("skal gå i dobbel løkke og ta ett element om gangen over til returnValue.....");
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				//System.out.println("t=" + t);
				//System.out.println("numberOfFirstAlignmentToDrop=" + numberOfFirstAlignmentToDrop);
				if (((TreeSet)(testElementNumbers[t])).size() > 0) {
					// there are elements to drop
					int numberOfFirstElementToDrop = ((Integer)(((TreeSet)(testElementNumbers[t])).first())).intValue();
					//System.out.println("numberOfFirstElementToDrop=" + numberOfFirstElementToDrop);
					int numberOfLastElementToDrop = ((Integer)(((TreeSet)(testElementNumbers[t])).last())).intValue();
					//System.out.println("numberOfLastElementToDrop=" + numberOfLastElementToDrop);
					for (int j=numberOfFirstElementToDrop; j<=numberOfLastElementToDrop; j++) {
						//System.out.println("drops element");
						//AElement elementToDrop = (AElement)elements[t].remove(elements[t].size()-1);
						((DefaultListModel)(returnValue.elements[t])).addElement((AElement)(elements[t].remove(numberOfFirstElementToDrop)));   // ###
					}
				}
			}
			// alignments starting with number 'numberOfFirstAlignmentToDrop' are to be dropped
			//System.out.println("skal gå i løkke og ta én alignment om gangen over til returnValue.alignments");
			while (alignments.size() > numberOfFirstAlignmentToDrop) {
				//System.out.println("drops alignment");
				returnValue.alignments.add(returnValue.alignments.size(), alignments.remove(numberOfFirstAlignmentToDrop));
			}
			// update aligned/total ratio in status line
			gui.statusLine.setMemoryUsage(gui.model.getMemoryUsage());
			gui.statusLine.setText(gui.model.updateAlignedTotalRatio());
			//
			return returnValue;
		}
	}

/*
From here on: Functions that are used by suggestWithoutGui
*/

	void pickUp(AlignmentsEtc valueGot, boolean scroll) {
		if (valueGot != null) {
			//######hvorfor tom løkke?
			for (int j=0; j<valueGot.alignments.size(); j++) {
				//System.out.println("skal legge til alignment nr " + ((Link)(valueGot.alignments.get(j))).alignmentNumber);
			}
			alignments.addAll(alignments.size(), valueGot.alignments);
			// elements
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				for (int i=0; i<((DefaultListModel)(valueGot.elements[t])).size(); i++) {
					elements[t].addElement(((AElement)((DefaultListModel)(valueGot.elements[t])).get(i)));   // ###
				}
			}
		}
	}
}
