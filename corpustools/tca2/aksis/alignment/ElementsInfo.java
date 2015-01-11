package aksis.alignment;

import java.util.Iterator;
import java.util.List;
import java.util.ArrayList;

/**
 * a list with information about alignable elements in one text.
 * doesn't span the whole text,
 * just a suitable range,
 * starting with the first element not yet aligned.
 * belongs to a Compare object
 */
class ElementsInfo {

	// which interval is stored
	// - first and last elementNumber, ikke sant?###
	int first = 0;
	int last = -1;
	// list of ElementInfo objects
	private List elementInfo = new ArrayList();

	public ElementsInfo() {
		//
	}

	public void purge() {
		first = 0;
		last = -1;
		elementInfo.clear();
	}

	//public ElementInfo getElementInfo(AlignmentModel model, int elementNumber, int t) {
	public ElementInfo getElementInfo(AlignmentModel model, int elementNumber, int t) throws EndOfTextException {

		//System.out.println("\ngetElementInfo. t = " + t + ", elementNumber = " + elementNumber);
		//System.out.println("getElementInfo. first = " + first + ", last = " + last);
		if (elementNumber < first) {
			// wanted element is outside range
			// expand range.
			//System.out.println("wanted element is outside range. expand range");
			setFirst(model, elementNumber, t);
			////setFirst(model, elementNumber, t, elementNumber);   // 2006-04-05
		} else if (elementNumber > last) {
			// wanted element is outside range - too high.
			// expand range.
			//System.out.println("wanted element is outside range - too high. expand range");
			try {
				setLast(model, elementNumber, t);
				////setLast(model, elementNumber, t, elementNumber);   // 2006-04-05
			} catch (EndOfTextException e) {
				throw e;
			}
		}
		//System.out.println("first = " + first + ", last = " + last);
		// debug
		ElementInfo temp = (ElementInfo)elementInfo.get(elementNumber - first);
		//System.out.println("getElementInfo. " + temp + "\n");
		// end debug
		return (ElementInfo)elementInfo.get(elementNumber - first);

	}

	/*
	public setElementInfo(int elementNumber, int t) {
		...
		element = ...[t]...;
		String text = XmlTools.getText(element);   ### heller bruke .getTextContent()
		elementInfo.set...
	}
	*/

	//public int getFirst(AlignmentModel model, int t) {
	public int getFirst() {
		return first;
	}

	/**
	  * change range - set a new start point
	  * update content accordingly.
	  */
	public void setFirst(AlignmentModel model, int newFirst, int t) {
	////public void setFirst(AlignmentModel model, int newFirst, int t, int elementNumber) {   // 2006-04-05
		//System.out.println("enter setFirst(). t = " + t + ", first = " + first + ", last = " + last + ", newFirst = " + newFirst);
		if (newFirst < first) {
			//System.out.println("setFirst(). tilfelle 1");
			List more = new ArrayList();
			for (int count = 0; count < first - newFirst; count++) {
				int index = newFirst + count;
				String text = model.nodes[t].item(index).getTextContent();

				more.add(new ElementInfo(model, text, t, index));   // index = elementNumber. ???? 20056-04-05
			}
			elementInfo.addAll(0, more);
			first = newFirst;
		} else if (newFirst > last) {
			//System.out.println("setFirst(). tilfelle 2");
			elementInfo.clear();
			first = newFirst;
			int husk = last;
			last = first - 1;
			//System.out.println("setFirst endret last fra " + husk + " til " + last);
		} else {
			//System.out.println("setFirst(). tilfelle 3");
			for (int count = 0; count < newFirst - first; count++) {
				//elementInfo.remove(first);   ### ugh
				elementInfo.remove(0);
			}
			first = newFirst;
		}
		//System.out.println("end setFirst(). t = " + t + ", first = " + first + ", last = " + last + ", newFirst = " + newFirst);
		//System.out.println("end setFirst(). ElementsInfo = " + ElementsInfo.this);
	}

	/**
	  * change range - set a new end point
	  * update content accordingly.
	  */
	//public void setLast(AlignmentModel model, int newLast, int t) {
	public void setLast(AlignmentModel model, int newLast, int t) throws EndOfTextException {
	////public void setLast(AlignmentModel model, int newLast, int t, int elementNumber) throws EndOfTextException {   // 2006-04-05

		//System.out.println("enter setLast(). t = " + t + ", first = " + first + ", last = " + last + ", newLast = " + newLast);
		if (newLast > last) {
			//System.out.println("setLast(). tilfelle 1");
			for (int count = 0; count < newLast - last; count++) {
				/*
				//Object element = ((AElement)(model.unaligned.elements[t].get(last + 1 + count))).element;  // ######################
				// last + 1 + count is absolute index.
				// calculate index relative unaligned.
				// ###### griseri. trenger metoder aligned.size(t) og toAlign.size(t)
				System.out.println("# aligned = " + model.aligned.elements[t].size());
				System.out.println("# to align = " + model.toAlign.elements[t].getSize());
				System.out.println("vil ha el nr " + (last + 1 + count) + " globalt");
				int index = last + 1 + count - (model.aligned.elements[t].size() + model.toAlign.elements[t].getSize());
				System.out.println("vil ha el nr " + index + " i unaligned");
				Object element = ((AElement)(model.unaligned.elements[t].get(index))).element;
				*/
				//String text = XmlTools.getText((Node)element);   ### heller bruke .getTextContent()
				int index = last + 1 + count;
				if (index >= model.nodes[t].getLength()) {
					last = index - 1 - count;
					//System.out.println("setter last = " + last + " (sjekk at verdien er riktig!), og throw'er en EndOfTextException");
					throw new EndOfTextException();
				}
				//String text = XmlTools.getText(model.nodes[t].item(index));
				String text = model.nodes[t].item(index).getTextContent();

				/* skal dette aktiveres her også?
				// 2006-9-15
				// ###replace all " by ' because of a bug in LineBreakMeasurer
				System.out.println("1");
				Pattern pattern = Pattern.compile("\"");
				Matcher matcher = pattern.matcher(text);
				text = matcher.replaceAll("'");
				// end 2006-9-15
				*/

				//elementInfo.add(new ElementInfo(model, text, t));
				elementInfo.add(new ElementInfo(model, text, t, index));   // index = elementNumber. ???? 2006-04-05
			}
			last = newLast;
		} else if (newLast < first) {
			//System.out.println("setLast(). tilfelle 2");
			elementInfo.clear();
			last = first - 1;
		} else {
			//System.out.println("setLast(). tilfelle 3");
			for (int count = 0; count < last - newLast; count++) {
				//elementInfo.remove(last - count);   ### ugh
				elementInfo.remove(last - first - count);
			}
			last = newLast;
		}
		//System.out.println("end setLast(). t = " + t + ", first = " + first + ", last = " + last + ", newLast = " + newLast);
		//System.out.println("end setLast(). ElementsInfo = " + ElementsInfo.this);
	}

	// ### for debuggingsformål

	public String toString() {
		StringBuffer ret = new StringBuffer();
		ret.append("[\n");
		Iterator it = elementInfo.iterator();
		while (it.hasNext()) {
			ElementInfo e = (ElementInfo)it.next();
			ret.append("" + e + "\n");
		}
		ret.append("]\n");
		return new String(ret);
	}

}

