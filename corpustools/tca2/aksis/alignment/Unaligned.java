package aksis.alignment;

import javax.swing.DefaultListModel;
import java.awt.Toolkit;

import java.util.Enumeration;
import org.w3c.dom.Node;

class Unaligned {

	/**
	 * lists of unaligned elements.
	 * one list for each text.
	 * shown in the gui's 'unaligned' JList components.
	 * each element is an AElement object.
	 */
	protected DefaultListModel[] elements;   // ########## private + get-metode er bedre

	Unaligned() {
		elements = new DefaultListModel[Alignment.NUM_FILES];
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			elements[t] = new DefaultListModel();
		}
	}

	public void purge() {
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			elements[t].clear();
		}
	}

	/**
	  * pop the top unaligned AElement of the t-th text
	  */
	AElement pop(int t) {

		if (elements[t].size() == 0) {
			Toolkit.getDefaultToolkit().beep();
			//System.out.println("BEEEEEEEEEEEEEEEEP Unaligned pop");
			System.out.println("Nothing to pop");
			return null;
		} else {
			return (AElement)elements[t].remove(0);
		}

	}

	/**
	  * insert an AElement at the top of the t-th text.
	  * set the element's state to unused,
	  * no matter what its previous state was.
	  */
	void catch_(int t, AElement element) {
		if (element != null) {
			element.alignmentNumber = -1;   // ¤¤¤bruke static konstant?
			elements[t].add(0, element);   // ### æsj. her trengs ingen (AElement)
		}
	}

	/**
	  * ...
	  */
	void add(int t, AElement element) {
		elements[t].addElement((Object)element);
	}

	public AElement get(int t, Node element) {
		// searches unaligned of text t
		// for an AElement containing a certain alignable element
		////Iterator it = elements[t].iterator();
		for (Enumeration en = elements[t].elements(); en.hasMoreElements();) {
			AElement test = (AElement)en.nextElement();
			if (test.element == element) {
				// success
				return test;
			}
		}
		// failure
		return null;
	}

}

