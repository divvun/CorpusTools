/*
 * AncestorFilter.java
 *
 * ...
 * ...
 * ...
 */

package aksis.alignment;

// Â¤Â¤Â¤ ikke sjekket nÃ¸yaktig hva vi trenger
import java.util.*;
import java.lang.String;

/**
 * used for newline format output.
 *
 * knows how much information about ancestor elements
 * should be prepended to the written version of the element.
 *
 * there are two different modes - MODE_ALLOW or MODE_DENY.
 * in each mode there is a list of names of elements
 * and a list of names of attributes
 * that will be allowed or denied.
 *
 * extreme cases:
 * MODE_ALLOW + empty element list = deny all.
 * MODE_DENY + empty element list = allow all.
 */
public class AncestorFilter {

	public static int MODE_ALLOW = 0;
	public static int MODE_DENY = 1;
	// for debugging
	private static String[] MODENAME = {"allow", "deny"};

	int mode;
	HashMap elementNames = new HashMap();
	HashMap attributeNames = new HashMap();

	AncestorFilter(int mode, String elementNamesString, String attributeNamesString) {

		setMode(mode);

		setElementNames(elementNamesString);

		setAttributeNames(attributeNamesString);

	}

	public boolean denyAll() {
		return ((mode == MODE_ALLOW) && (elementNames.size() == 0));
	}

	public boolean allowElement(String elementName) {
		if (mode == MODE_ALLOW) {
			return elementNames.containsKey(elementName);
		} else {
			return !elementNames.containsKey(elementName);
		}
	}

	public boolean allowAttribute(String elementName, String attributeName) {
		// first check if element is allowed.
		// can't allow attribute if the element is denied
		if (allowElement(elementName)) {
			if (mode == MODE_ALLOW) {
				return attributeNames.containsKey(attributeName);
			} else {
				return !attributeNames.containsKey(attributeName);
			}
		} else {
			return false;
		}
	}

	public boolean noElements() {
		return (elementNames.size() == 0);
	}

	// ###dodgy? can one really set mode without consulting and perhaps changing the element names list?
	// ###bestemmer at jeg skal la dette vÃ¦re kallende kodes ansvar
	public void setMode(int mode) {
		this.mode = mode;
	}

	public void setElementNames(String names) {
		elementNames.clear();
		String[] temp = names.trim().split(" ");
		for (int i=0; i<temp.length; i++) {
			String name = temp[i];
			if (name != "") {
				elementNames.put(name, true);
			}
		}
	}

	public void setAttributeNames(String names) {
		attributeNames.clear();
		String[] temp = names.trim().split(" ");
		for (int i=0; i<temp.length; i++) {
			String name = temp[i];
			if (name != "") {
				attributeNames.put(name, true);
			}
		}
	}

	public String getElementNamesAsString() {
		String string = "";
		boolean first = true;
		Iterator it = elementNames.keySet().iterator();
		while (it.hasNext()) {
			if (first) {
				first = false;
			} else {
				string += " ";
			}
			string += (String)it.next();
		}
		return string;
	}

	public String getAttributeNamesAsString() {
		String string = "";
		boolean first = true;
		Iterator it = attributeNames.keySet().iterator();
		while (it.hasNext()) {
			if (first) {
				first = false;
			} else {
				string += " ";
			}
			string += (String)it.next();
		}
		return string;
	}

	// for debugging
	private String getModeAsString() {
		return MODENAME[mode];
	}

	// for debugging
	public String toString() {
		return "mode: " + getModeAsString() + ", elements: " + getElementNamesAsString() + ", attributes: " + getAttributeNamesAsString();
	}

}



