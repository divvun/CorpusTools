/*
 * Skip.java
 *
 * ...
 * ...
 * @author Oystein Reigem
 */

package aksis.alignment;

import javax.swing.DefaultListModel;

class Skip {

	// get next available element from text t.
	// the next available element is the topmost one
	// that hasn't been included in someAligned yet
	public static AElement getNextAvailableUnalignedElement(Unaligned unaligned, AlignmentsEtc someAligned, int t) {
		if (unaligned.elements[t].size() == 0) {
			// no unalignable elements. therefore no available ones
			//System.out.println("getNextAvailableUnalignedElement. no unalignable elements. therefore no available ones");
			return null;
		} else {
			boolean done = false;
			int next = 0;
			while (!done) {
				// check next unaligned element
				AElement aElement = (AElement)unaligned.elements[t].get(next);
				if (((DefaultListModel)someAligned.elements[t]).contains(aElement)) {
					// already used. not available
					next++;
					if (next > unaligned.elements[t].size()-1) {
						// run out of unaligned elements.
						// no available elements among the unaligned ones
						//System.out.println("getNextAvailableUnalignedElement. run out of unaligned elements. no available elements among the unaligned ones");
						return null;
					}
				} else {
					// available
					//System.out.println("getNextAvailableUnalignedElement. available");
					return aElement;
				}

			}
			// this statement will never be reached
			//System.out.println("getNextAvailableUnalignedElement. this statement will never be reached");
			return null;
		}
	}

}

