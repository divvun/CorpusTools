package aksis.alignment;

import javax.swing.DefaultListModel;

import java.util.List;
import java.util.ArrayList;
import java.util.TreeSet;
import java.util.Iterator;

/**
 * a class that bundles alignments with their AElement elements.
 * used for movement of data between aligned and to-align (alignments under manual consideration).
 * ###also used for movement of data from unaligned to toAlign when skipping half-aligned file
 * ###ikke god. redundans og mulighet for inkonsistens i alignments vs elements.
 */
class AlignmentsEtc {

	//List alignments = new ArrayList();
	List<Link> alignments = new ArrayList<Link>();   // 2006-11-20
	Object[] elements;

	AlignmentsEtc() {
		elements = new DefaultListModel[Alignment.NUM_FILES];
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			elements[t] = new DefaultListModel();
		}
	}

	// ###brukes ikke overalt

	public void add(Link link) {
		alignments.add(link);
	}

	// ###brukes ikke overalt
	//public void add(int t, Element element) {
	public void add(int t, AElement element) {
		if (!((DefaultListModel)elements[t]).contains(element)) {
			((DefaultListModel)elements[t]).addElement(element);
		}
	}

	public boolean hasHoles() {

		//TreeSet[] testElementNumbers = new TreeSet[Alignment.NUM_FILES];   // TreeSet is a sorted Set
		TreeSet<Integer>[] testElementNumbers;   // 2006-11-20
		testElementNumbers= new TreeSet[Alignment.NUM_FILES];   // TreeSet is a sorted Set   // 2006-11-20
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			//testElementNumbers[t] = new TreeSet();
			testElementNumbers[t] = new TreeSet<Integer>();   // 2006-11-20
		}

		// loop through the alignments
		Iterator it = alignments.iterator();
		while(it.hasNext()) {
			Link link = (Link)it.next();
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				Iterator it2 = link.getElementNumbers(t).iterator();
				while(it2.hasNext()) {
					Integer n = (Integer)it2.next();
					testElementNumbers[t].add(n);
				}
			}
		}

		// ###the hasHoles method should have been a utility thing,
		// not belong to the Aligned object.
		//###uh. Aligned's hasHoles is more complicated
		//return Aligned.hasHoles(testElementNumbers);
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			if (testElementNumbers[t].size() > 0) {
				int last = ((Integer)(testElementNumbers[t].last())).intValue();
				int first = ((Integer)(testElementNumbers[t].first())).intValue();
				if ((last - first + 1) != testElementNumbers[t].size()) {
					// found hole for text t
					return true;
				}
			}
		}
		// found no hole for any text
		return false;

	}

	public boolean empty() {
		return (alignments.size() == 0);
	}

	// for debugging purposes
	public void print() {
		// loop through the alignments
		Iterator it = alignments.iterator();
		System.out.println("<<<link");
		while(it.hasNext()) {
			Link link = (Link)it.next();
			System.out.println(link);
		}
		System.out.println("link>>>");
		// loop ... elements
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			System.out.println("<<<text " + t);
			DefaultListModel l = (DefaultListModel)elements[t];
			for (int i=0; i<l.size(); i++) {
				System.out.println(l.get(i));
			}
			System.out.println("text " + t + ">>>");
		}
	}

}
