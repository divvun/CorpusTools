package aksis.alignment;

import javax.swing.DefaultListModel;
import java.awt.Toolkit;

import java.util.List;
import java.util.ArrayList;
import java.util.TreeSet;
import java.util.Collections;
import java.util.Iterator;

class ToAlign {

	/**
	 * lists of elements under consideration for alignment.
	 * one list for each text.
	 * shown in the gui's 'toAlign' JList components.
	 * each element is an AElement object.
	 */
	protected DefaultListModel[] elements;

	/**
	 * 0 or more alignments.
	 * each alignment is a Link object.
	 */
	//private List pending = new ArrayList();
	private List<Link> pending = new ArrayList<Link>();   // 2006-11-20

	///**
	// * the unaligned elements.
	// * also represented by a Link object.
	// */
	//private Link unused = new Link();

	/**
	 * the number of the first pending alignment.
	 * if no alignments pending, the number to use when establishing a pending alignment,
	 * i.e, one higher than the highest number of the finished alignments.
	 */
	private int firstAlignmentNumber = 0;

	ToAlign() {
		elements = new DefaultListModel[Alignment.NUM_FILES];
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			elements[t] = new DefaultListModel();
		}
	}

	public void purge() {
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			elements[t].clear();
		}
		pending.clear();
		firstAlignmentNumber = 0;
	}

	/**
	 * is all (both) to-align boxes empty?
	 */
	boolean empty() {
		//System.out.println("ToAlign.empty() kalt");
		//System.out.println("pending.size() = " + pending.size());
		//System.out.println("unused.empty() = " + unused.empty());
		//return (pending.size() == 0 && unused.empty());
		return (pending.size() == 0);
	}

	/**
	 * is to-align box number t empty?
	 */
	// ###needed for correction of bug 2006-03-28
	// ###kanskje bedre å kikke i boksens liste...
	boolean empty(int t) {
		// search through pending alignments for one that has element(s) in text t
		for (int ii=0; ii < pending.size(); ii++) {
			Link link = (Link)(pending.get(ii));
			if (link.elementNumbers[t].size() > 0) {
				// found one
				return false;
			}
		}
		// searched through all but found none
		return true;
	}

	// #######bør sikkert brukes mer

	int pendingCount() {
		return pending.size();
	}

	// ¤¤¤ 2004-10-31. brukes ikke - i hvert fall ikke for øyeblikket
	void link(AlignGui gui, int t, int indexClicked, int elementNumberClicked) {   // package access
		// link by default to uppermost pending alignment
		//System.out.println("firstAlignmentNumber = " + firstAlignmentNumber);
		link(gui, t, indexClicked, elementNumberClicked, firstAlignmentNumber);
	}

	// ¤¤¤ 2004-10-31. bare denne brukes.
	// ¤¤¤ denne programmeringen trenger sikkert rydding.
	// for mye som ikke er oop?
	void link(AlignGui gui, int t, int indexClicked, int elementNumberClicked, int alignmentNumberToLinkTo) {   // package access
		//System.out.println("ToAlign sin link()");
		//System.out.println("pending før at link() har gjort sin jobb:");
		for (int ii=0; ii < pending.size(); ii++) {
			//System.out.println("pending alignment nr " + ii + " er " + (Link)(pending.get(ii)));
		}
		// ¤¤¤foreløpig
		// redundans: indexClicked (nr på item i JList) og elementNumberClicked
		//System.out.println("indexClicked = " + indexClicked);
		//System.out.println("elementNumberClicked = " + elementNumberClicked);
		//System.out.println("alignmentNumberToLinkTo = " + alignmentNumberToLinkTo);
		//System.out.println("t = " + t);
		// clicked on unused or pending? ¤¤¤ skal ikke være noen unused lenger. i.g.n.m
		int alignmentNumberClicked = ((AElement)(elements[t].get(indexClicked))).alignmentNumber;
		//System.out.println("alignmentNumberClicked = " + alignmentNumberClicked);
		// ...
		int lastAlignmentNumber = firstAlignmentNumber + pending.size() - 1;
		//System.out.println("lastAlignmentNumber = " + lastAlignmentNumber);
		// ...
		//System.out.println("håndtering av alignmentNumberToLinkTo == -2");
		if (alignmentNumberToLinkTo == -2) {
			// -2 is a signal to link to the next available alignment
			if (   (alignmentNumberClicked == lastAlignmentNumber)
			    && (((Link)(pending.get(lastAlignmentNumber - firstAlignmentNumber))).countElements() <= 1)) {   // == 1
			    //System.out.println("has run out of alignments. back to the first one");
			    // has run out of alignments.
			    // back to the first one
			    //alignmentNumberToLinkTo = 0; ###
			    alignmentNumberToLinkTo = firstAlignmentNumber;
			} else {
			    //System.out.println("not run out of alignments");
				alignmentNumberToLinkTo = alignmentNumberClicked + 1;
				//System.out.println("alignmentNumberToLinkTo = " + alignmentNumberToLinkTo);
			}
		}
		//System.out.println("alignmentNumberToLinkTo = " + alignmentNumberToLinkTo);
		// might have to create new pending
		if (alignmentNumberToLinkTo > pending.size() - 1) {
			pending.add(new Link());
		}
		// change alignment
		//System.out.println("change alignment. alignment før = " + (Link)(pending.get(alignmentNumberClicked - firstAlignmentNumber)));
		//System.out.println("t = " + t);
		//System.out.println("alignmentNumberClicked = " + alignmentNumberClicked);
		//System.out.println("elementNumberClicked = " + elementNumberClicked);
		//System.out.println("firstAlignmentNumber = " + firstAlignmentNumber);
		//System.out.println("alignmentNumberToLinkTo = " + alignmentNumberToLinkTo);
		((Link)(pending.get(alignmentNumberClicked - firstAlignmentNumber))).elementNumbers[t].remove(new Integer(elementNumberClicked));
		//((Link)(pending.get(alignmentNumberClicked - firstAlignmentNumber))).elementNumbers[t].remove(new Integer(indexClicked));   // endret 2005-05-31. nei, det er tull. vi jobber på et Set, der nøklene er elementnummer, ikke indeks
		((Link)(pending.get(alignmentNumberToLinkTo - firstAlignmentNumber))).elementNumbers[t].add(new Integer(elementNumberClicked));
		//((Link)(pending.get(alignmentNumberToLinkTo - firstAlignmentNumber))).elementNumbers[t].add(new Integer(indexClicked));   // endret 2005-05-31. nei, det er tull. vi jobber på et Set, der nøklene er elementnummer, ikke indeks
		//((Link)(pending.get(alignmentNumberToLinkTo - firstAlignmentNumber))).alignmentNumber = alignmentNumberToLinkTo;
		//System.out.println("change alignment. alignment etter = " + (Link)(pending.get(alignmentNumberClicked - firstAlignmentNumber)));
 		// check if the change creates a hole in the list of pending alignments,
		// i.e, a pending alignment with no elements.
		// if so, remove hole
		//System.out.println("sjekk om hull");
		for (int ii=0; ii < pending.size(); ) {
			if (((Link)(pending.get(ii))).countElements() == 0) {
				// hole. remove
				// ### 2006-03-30.
				// ### oppdaget at jeg et _annet_ sted tok pending.remove(...) med fatale konsekvenser.
				// ### det ble nemlig hull i nummereringen av alignments.
				// ### (man droppet et element som ikke var linket mot noe annet element
				// ### (det inngikk altså i en 1-0- eller 0-1-alignment),
				// ### og da forsvant hele alignmenten,
				// ### men jeg hadde ikke tenkt på at jeg da måtte renummerere
				// ### de etterfølgende alignments i pending.
				// ### men her på _dette_ stedet rydder jeg vel grundig opp?
				pending.remove(ii);
				// (repeat with same ii)
			} else {
				ii++;
			}
		}
		// try to maintain a natural order to the pending alignments.
		//
		// there might not exist a canonical natural order
		// for alignments, though.
		// say two texts contain elements that are cross-aligned like this:
		//   A     B
		//   B     A
		// what is the natural order of the alignments?
		//
		// is it A before B?:
		//   A--A  B
		//       \/
		//       /\
		//   B--B  A
		//
		// or is it B before A?:
		//   A  B--B
		//    \/
		//    /\
		//   B  A--A
		//
		// the programming here will let the order be decided by the first text,
		// i.e, let the order of alignments be decided by the order
		// of their elements in the first text:
		//   A--A  B
		//       \/
		//       /\
		//   B--B  A
		//
		// a more precise rule is needed when alignments
		// have more than one element in each text:
		// then the order is decided by each alignment's
		// *first* element in the first text.
		//
		// alignments without any elements in the first text
		// might be more problematic.
		// example:
		// A      B
		// B      C
		//        A
		//
		// the programming here will put all alignments
		// with elements in the first text
		// before alignments without any elements in the first text:
		//   A--A  B
		//       \/
		//       /\
		//   B--B  A
		//
		//      C--C
		//
		// the latter alignments' order is decided by the order
		// of the elements in the second text.
/*
skitt
A B
A A
her havner B sist
her er det ikke noe som krysser.
det kan gjøre det lettere
eller overlate fullstendig til brukeren?
*/
		//System.out.println("prøv å bevare naturlig rekkefølge");
		//List toSort = new ArrayList();
		List<String> toSort = new ArrayList<String>();   // 2006-11-20
		for (int ii=0; ii < pending.size(); ii++) {
			// next pending alignment
			//System.out.println("next pending alignment. ii=" + ii);
			Link link = (Link)(pending.get(ii));
			// find this alignment's first text
			for (int tt=0; tt<Alignment.NUM_FILES; tt++) {
				if (link.elementNumbers[tt].size() > 0) {
					//System.out.println("make sort criteria for the alignment");
					// make sort criteria for the alignment
					int firstElementNumber = ((Integer)(((TreeSet)(link.elementNumbers[tt])).first())).intValue();
					//System.out.println("firstElementNumber = " + firstElementNumber);
					// ¤¤¤ right just zero fill ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤
					String firstElementNumberString = Integer.toString(1000000 + firstElementNumber).substring(1);
					//System.out.println("firstElementNumberString = " + firstElementNumberString);
					toSort.add(Integer.toString(tt) + "-" + firstElementNumberString + "-" + ii);
					break;
				}
			}
		}
		// sort
		//List sorted = new ArrayList();
		List<String> sorted = new ArrayList<String>();   // 2006-11-20
		Collections.sort(toSort);
		sorted = toSort;
		// reorder the pending alignments
		//List newPending = new ArrayList();
		List<Link> newPending = new ArrayList<Link>();   // 2006-11-20
		for (int ii=0; ii < sorted.size(); ii++) {
			//System.out.println("neste sorterte. ii=" + ii);
			String tempStr = (String)(sorted.get(ii));
			//System.out.println("tempStr = " + tempStr);
			String[] tempArr = tempStr.split("-");
			int tempInt = Integer.parseInt(tempArr[2]);
			//System.out.println("tempInt = " + tempInt);
			newPending.add(pending.get(tempInt));
			//((Link)(newPending.get(ii))).alignmentNumber = ii;
			((Link)(newPending.get(ii))).alignmentNumber = ii + gui.model.aligned.alignments.size();   // endret 2005-05-31. bug som har overlevd lenge. har visst ikke prøvd toAlign-klikking når det står noe i aligned. alignmentnummer i toAlign starter på # aligned alignments, ikke nødvendigvis på 0
		}
		//System.out.println("pending før sort =");
		for (int ii=0; ii < pending.size(); ii++) {
			//System.out.println("pending.get(" + ii + ") =" + (Link)(pending.get(ii)));
		}
		pending = newPending;
		//System.out.println("pending etter sort =");
		for (int ii=0; ii < pending.size(); ii++) {
			//System.out.println("pending.get(" + ii + ") =" + (Link)(pending.get(ii)));
		}
		// update and refresh elements
		for (int ii=0; ii < pending.size(); ii++) {
			//System.out.println("neste refresh elements");
			for (int tt=0; tt<Alignment.NUM_FILES; tt++) {
				//System.out.println("tt=" + tt);
				Iterator e = ((TreeSet)(((Link)(pending.get(ii))).getElementNumbers(tt))).iterator();
				//System.out.println("skaffet iterator");
				while (e.hasNext()) {
					//System.out.println("har en neste");
					int elementNumber = ((Integer)(e.next())).intValue();
					//System.out.println("elementNumber=" + elementNumber);
					int index = elementNumber - gui.model.aligned.elements[tt].size();   // endret 2005-05-31. bug som har overlevd lenge. har visst ikke prøvd toAlign-klikking når det står noe i aligned
					//((AElement)(elements[tt].get(elementNumber))).alignmentNumber = ((Link)(pending.get(ii))).alignmentNumber;
					((AElement)(elements[tt].get(index))).alignmentNumber = ((Link)(pending.get(ii))).alignmentNumber;   // endret 2005-05-31. bug som har overlevd lenge. har visst ikke prøvd toAlign-klikking når det står noe i aligned
					// shake it so the colour changes (remove + add)
					//elements[tt].add(elementNumber ,elements[tt].remove(elementNumber));
					elements[tt].add(index, elements[tt].remove(index));   // endret 2005-05-31. bug som har overlevd lenge. har visst ikke prøvd toAlign-klikking når det står noe i aligned
				}
			}
		}
		//System.out.println("pending etter at link() har gjort sin jobb:");
		for (int ii=0; ii < pending.size(); ii++) {
			//System.out.println("pending alignment nr " + ii + " er " + (Link)(pending.get(ii)));
		}

	}

	//AElement drop(int t) {
	AElement drop(AlignGui gui, int t) {   // ### 2006-03-30
		//System.out.println("AElement.drop(). t = " + t);
		//if (empty()) {
		if (empty(t)) {   // ###bug corrected 2006-03-28
			Toolkit.getDefaultToolkit().beep();
			//System.out.println("BEEEEEEEEEEEEEEEEP ToAlign drop");
			//System.out.println("Nothing to drop");
			return null;
		} else {
			//System.out.println("elements[t].size() = " + elements[t].size());
			AElement elementToDrop = (AElement)elements[t].remove(elements[t].size()-1);
			//System.out.println("elementToDrop = " + elementToDrop);
			//System.out.println("elements[t].size() = " + elements[t].size());
			if (elementToDrop.alignmentNumber == -1) {
				// the element to drop is unused
				//unused.elementNumbers[t].remove(new Integer(elementToDrop.elementNumber));
				System.out.println("*** Program error ***");
			} else {
				// the element to drop is pending.
				// where in the 'pending' list is its Link?
				//System.out.println("elementToDrop.alignmentNumber = " + elementToDrop.alignmentNumber);
				//System.out.println("((Link)(pending.get(0))).alignmentNumber = " + ((Link)(pending.get(0))).alignmentNumber);
				int index = elementToDrop.alignmentNumber - ((Link)(pending.get(0))).alignmentNumber;
				//System.out.println("index = " + index);
				// remove element from its pending alignment
				((Link)(pending.get(index))).getElementNumbers(t).remove(new Integer(elementToDrop.elementNumber));
				// check if there is anything left of the pending alignment
				//System.out.println("check if there is anything left of the pending alignment");
				if (((Link)(pending.get(index))).empty()) {
					// nothing. remove it
					//System.out.println("nothing. remove it");
					pending.remove(index);
					// ### 2006-03-30.
					// renumber the pending alignments that follow!
					for (int ii=index; ii < pending.size(); ii++) {
						((Link)(pending.get(ii))).alignmentNumber--;
						// don't forget to update the alignment numbers
						// in the elements that belong to this alignment
						for (int tt=0; tt<Alignment.NUM_FILES; tt++) {
							Iterator e = ((TreeSet)(((Link)(pending.get(ii))).getElementNumbers(tt))).iterator();
							while (e.hasNext()) {
								int elementNumber = ((Integer)(e.next())).intValue();
								int indexx = elementNumber - gui.model.aligned.elements[tt].size();
								((AElement)(elements[tt].get(indexx))).alignmentNumber = ((Link)(pending.get(ii))).alignmentNumber;
								// shake the element so the colour changes (remove + add)
								elements[tt].add(indexx, elements[tt].remove(indexx));
							}
						}
					}
				}
			}
			return elementToDrop;
		}
	}

	void pickUp(int t, AElement element) {
		if (element != null) {
			elements[t].add(elements[t].size(), element);
			if (pending.size() == 0) {
				pending.add(new Link());
				((Link)(pending.get(0))).alignmentNumber = firstAlignmentNumber;
			}
			((Link)(pending.get(pending.size() - 1))).elementNumbers[t].add(new Integer(element.elementNumber));
			int lastAlignmentNumber = firstAlignmentNumber + pending.size() - 1;
			element.alignmentNumber = lastAlignmentNumber;
		}
	}

	// ###ment for å ta imot fra aligned, men vil bruke det for someAligned også?
	void catch_(AlignmentsEtc valueGot) {
		if (valueGot != null) {
			// alignments
			//System.out.println("valueGot.alignments.size() = " + valueGot.alignments.size());
			//System.out.println("tar pending.addAll(...)");
			pending.addAll(0, valueGot.alignments);
			// elements
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				//System.out.println("((DefaultListModel)(valueGot.elements[" + t + "])).size() = " + ((DefaultListModel)(valueGot.elements[t])).size());
				for (int i=0; i<((DefaultListModel)(valueGot.elements[t])).size(); i++) {
					//System.out.println("skal ta elements[t].add(" + i + ", ...)");
					//System.out.println("testDefaultListModel");
					DefaultListModel testDefaultListModel = (DefaultListModel)(valueGot.elements[t]);
					//System.out.println("tester testObject");
					Object testObject = ((DefaultListModel)(valueGot.elements[t])).get(i);
					//System.out.println("tester testAElement");
					AElement testAElement = (AElement)(((DefaultListModel)(valueGot.elements[t])).get(i));
					//System.out.println("har testet testAElement");
					elements[t].add(i, (AElement)(((DefaultListModel)(valueGot.elements[t])).get(i)));   // ###
				}
			}
			firstAlignmentNumber = ((Link)(pending.get(0))).alignmentNumber;
			//System.out.println("nå ble firstAlignmentNumber = " + firstAlignmentNumber);
		}
	}

	/**
	 * pops everything,
	 */
	AlignmentsEtc flush() {
		//System.out.println("flush A");
		//MemTest.print("Tenured Gen", "");
		//if (!unused.empty()) {
		//	// ...
		//	//System.out.println("unused ikke tom");
		//	Toolkit.getDefaultToolkit().beep();
		//	System.out.println("Program error. 'unused' not empty");
		//	//System.out.println("BEEEEEEEEEEEEEEEEP ToAlign flush 1");
		//	return null;
		//} else {
			//System.out.println("unused tom");
			//System.out.println("flush B");
			//MemTest.print("Tenured Gen", "");
			if (pending.size() == 0) {
				//System.out.println("pending tom");
				Toolkit.getDefaultToolkit().beep();
				System.out.println("Nothing to flush");
				//System.out.println("BEEEEEEEEEEEEEEEEP ToAlign flush 2");
				return null;
			} else {
				//System.out.println("skal flushe");
				// update firstAlignmentNumber
				firstAlignmentNumber = ((Link)(pending.get(pending.size() - 1))).alignmentNumber + 1;
				//System.out.println("flush. nå ble firstAlignmentNumber = " + firstAlignmentNumber);
				// update ...
				//System.out.println("flush C");
				//MemTest.print("Tenured Gen", "");
				AlignmentsEtc returnValue = new AlignmentsEtc();
				//System.out.println("flush D");
				//MemTest.print("Tenured Gen", "");
				while (pending.size() > 0) {
					returnValue.alignments.add(pending.remove(0));
					//System.out.println("flush E");
					//MemTest.print("Tenured Gen", "");
				}
				//System.out.println("nå er pending.size() = " + pending.size());
				for (int t=0; t<Alignment.NUM_FILES; t++) {
					//((DefaultListModel)(returnValue.elements[t])).addAll((DefaultListModel)(elements[t]));
					while (((DefaultListModel)(elements[t])).size() > 0) {
						((DefaultListModel)(returnValue.elements[t])).addElement((AElement)(elements[t].remove(0)));
						//System.out.println("flush F");
						//MemTest.print("Tenured Gen", "");
					}
					//System.out.println("nå er elements[" + t + "].size() = " + elements[t].size());
				}
				//System.out.println("flush G");
				//MemTest.print("Tenured Gen", "");
				return returnValue;
			}
		//}
	}

}
