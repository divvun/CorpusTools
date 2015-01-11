package aksis.alignment;

import java.awt.Color;

import org.w3c.dom.Node;
import org.w3c.dom.Attr;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.DOMException;

/**
 * the program works with elements from xml files, e.g sentences.
 * each element is a node in a DOM tree.
 * but the program also needs to know which alignment each element is involved in, if any.
 * for this purpose the AElement object knows not only the element
 * but also the element's sequence number and the number of the alignment.
 */
class AElement {

	public static final int NUM_COLORS = 10;   // foreløpig ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤

	/**
	 * the element itself.
	 * a node in a DOM tree for the current text.
	 */
	Node element;

	/**
	 * the sequence number of the element.
	 * the elements of a text are numbered 0, 1, 2, 3, ...
	 */
	int elementNumber;

	/**
	 * the number of the alignment the element is involved in.
	 * alignments have a global numbering 0, 1, 2, 3, ...
	 * #####################################################unused elements under consideration have a special value -1.
	 */
	int alignmentNumber;

	/**
	 * the length in characters of the text content of the element. ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ burde normalisert whitespace
	 */
	int length;

	AElement(Node o, int en) {
		element = o;
		elementNumber = en;
		alignmentNumber = -1;   // ¤¤¤ not used yet
		//length = XmlTools.getText(element).length();
		length = element.getTextContent().length();
	}

	public Color getColor() {
		//System.out.println("getColor. alignmentNumber = " + alignmentNumber);
		if (alignmentNumber == -1) {
			//return Color.white;
			return Color.getHSBColor((float)0.00, (float)0.00, (float)0.97);
		} else {
			return Color.getHSBColor((float)((float)alignmentNumber / NUM_COLORS), (float)0.13, (float)1.00);
		}
	}

	/**
	 * makes a value that keeps - but normalizes - the division into lines of the element.
	 * ¤¤¤because some files can have odd line endings.
	 * if this value is rendered in a list box as a one-line thing it will not wrap.
	 * if this value is rendered in a list box as a multi-line thing it will wrap at line endings.
	 * ¤¤¤ ¤¤¤ ¤¤¤ suddenly wrap works after all! and this method isn't used!
	 * ¤¤¤ fixed
	 */
	public String toString() {
		return XmlTools.getXmlContent(element);   // 2006-09-19
	}

	// ###some users might like parent info prepended to the elements
	// in their newline format output files.
	// this method makes a suitable version for that purpose
	public String toNewString(AncestorFilter filter) {

		//Pattern pattern = Pattern.compile("[\\n\\r]+");   // pattern = [\n\r]+ , i.e, matches all kinds of line endings, also multiple endings
		//Matcher matcher = pattern.matcher(XmlTools.getXmlContent(element));   // ¤¤¤just the text, e.g, 'Blah blah blah'

		//#### skal dette ut i XmlTools?

		Node current = element;
		//short test2 = element.getNodeType();   //###debug
		String pathText = "";

		if (!filter.denyAll()) {

			String ancestorInfo;
			NamedNodeMap attrs;
			String elementName;
			Attr attribute;
			boolean done = false;
			//short test = Node.ELEMENT_NODE;   //###debug
			while (!done) {
				// next parent?
				try {
					current = current.getParentNode();
				} catch (DOMException e) {
					done = true;
				}
				// ???
				if (current == null) {
					done = true;
				} else {
					// but stop before root element is reached
					try {
						Node test = current.getParentNode();
						if (test.getNodeName() == "#document") {
							done = true;
						}
					} catch (DOMException e) {
						done = true;
					}
				}
				if (!done) {
					if (current.getNodeType() == Node.ELEMENT_NODE) {
						//
						elementName = current.getNodeName();
						if (filter.allowElement(elementName)) {
							ancestorInfo = "<" + elementName;
							attrs = current.getAttributes();
							for (int i = 0; i < attrs.getLength(); i++) {
								attribute = (Attr)attrs.item(i);
								if (filter.allowAttribute(elementName, attribute.getName())) {
									ancestorInfo += " " + attribute.getName() + "='" + attribute.getValue() + "'";
								}
							}
							ancestorInfo += ">";
							pathText = ancestorInfo + " " + pathText;
						}
					}
				}
			}

		}

		//return pathText + matcher.replaceAll(" ");   // §§§
		return pathText + XmlTools.getXmlContent(element);   // 2006-09-19 (nå skal elementet inneholde tekst uten (særlig) unødig whitespace)

	}

}
