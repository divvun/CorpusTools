/*
 * Utils.java
 *
 * ...
 * ...
 * @author Oystein Reigem
 */

package aksis.alignment;

import java.text.*;   // AttributedString, AttributedCharacterIterator
import java.awt.font.*;   // LineBreakMeasurer
import java.awt.*;
import java.lang.Math.*;
import java.util.*;

class Utils {

	// ### hadde jeg problemer med Ã¥ ha denne metoden her?

	// ### fordi jeg ikke skjÃ¸nte at den mÃ¥tte deklareres static?

	// ### se do to andre metodene
	/*
	public boolean hasHoles(Set[] integerSet) {

		// used to check if the n latest finished alignments
		// (the n bottom alignments)
		// have any holes.
		// for each text see if there are holes
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			//System.out.println("t=" + t);
			if (((TreeSet)(integerSet[t])).size() > 0) {
				// there are elements in this text covered by the n latest alignments.
				// find the number of the highest element aligned for this text.
				// note that there might be crossing alignments,
				// so this element might not be covered by the n latest ones
				int high = ((AElement)(elements[t].get(elements[t].size()-1))).elementNumber;
				//System.out.println("high=" + high);
				// find the number of the lowest element covered by the n latest alignments
				int low = ((Integer)(((TreeSet)(integerSet[t])).last())).intValue();
				//System.out.println("low=" + low);
				// is there a hole?
				if (((TreeSet)(integerSet[t])).size() < (high-low+1)) {
					// yes
					//System.out.println("her er et hull");
					return true;
				}
			}
		}
		// no holes found
		//System.out.println("fant ingen hull");
		return false;

	}
	*/

	public static boolean overlaps(int pos, int len, int otherPos, int otherLen) {
		// checks if two integer intervals overlap.
		// the first interval is {pos, pos+1, ..., pos+len-1}.
		// the other interval is {otherPos, otherPos+1, ..., otherPos+otherLen-1}
		return ((pos <= otherPos + otherLen - 1) && (otherPos <= pos + len - 1));
	}

	public static int countWords(String str) {
		// ######### for this method to work
		// str must have space delimited words and no extra space anywhere!
		if (str.length() == 0) {
			return 0;
		} else {
			int count = 1;
			for (int i = 0; i < str.length(); i++) {
				if (str.charAt(i) == ' ') {
					count++;
				}
			}
			return count;
		}
	}

	// ===
	// #######tatt fra <http://www.rgagnon.com/javadetails/java-0306.html>.
	// #######men finnes det virkelig ikke en slik metode i java? finner den ikke

	public static String stringToHTMLString(String string) {

		StringBuffer sb = new StringBuffer(string.length());
		// true if last char was blank // #######jeg trenger sikkert ikke whitespcehÃ¥ndteringen, men
		boolean lastWasBlankChar = false;
		int len = string.length();
		char c;

		for (int i = 0; i < len; i++) {
			c = string.charAt(i);
			if (c == ' ') {
				// blank gets extra work,
				// this solves the problem you get if you replace all
				// blanks with &nbsp;, if you do that you loss
				// word breaking
				if (lastWasBlankChar) {
					lastWasBlankChar = false;
					sb.append("&nbsp;");
				} else {
					lastWasBlankChar = true;
					sb.append(' ');
				}
			} else {
				lastWasBlankChar = false;
				//
				// HTML Special Chars
				if (c == '"')
					sb.append("&quot;");
				else if (c == '&')
					sb.append("&amp;");
				else if (c == '<')
					sb.append("&lt;");
				else if (c == '>')
					sb.append("&gt;");
				else if (c == '\n')
					// Handle Newline
					sb.append("&lt;br/&gt;");
				else {
					int ci = 0xffff & c;
					if (ci < 160 )
						// nothing special only 7 Bit
						sb.append(c);
					else {
						// Not 7 Bit use the unicode system
						sb.append("&#");
						sb.append(new Integer(ci).toString());
						sb.append(';');
					}
				}
			}
		}
		return sb.toString();

	}

	// ###modifisert fra kode funnet pÃ¥ <http://lists.ximian.com/pipermail/mono-patches/2006-January/068937.html>

	// ##############brukes visst ikke (oppdaget 2006-12-08)

	//public static int wrappedTextHeight(String text, Font font, int width) {
	public static int wrappedTextHeight(String text, Graphics2D g, int width) {   // 2006-09-15

		//System.out.println("\ntext=" + text);   // 2006-09-15
		//System.out.println("getTime()=" + (new Date()).getTime());   // 2006-12-08

		Font font = g.getFont();

		// construct an attributed string instance with the given text
		java.text.AttributedString attrString = new java.text.AttributedString(text);
		// add font attribute to the entire text
		attrString.addAttribute(java.awt.font.TextAttribute.FONT, font);
		// get iterator for the attributed string
		java.text.AttributedCharacterIterator it = attrString.getIterator();
		int itStart = it.getBeginIndex();
		int itEnd   = it.getEndIndex();
		// construct a LineBreakMeasurer for the text.
		// #############grrrrrrrrrrrr bug in LineBreakMeasurer? breaks at space
		// but also after other characters like "'.!!!!!!!!
		java.awt.font.LineBreakMeasurer lineMeasurer = new java.awt.font.LineBreakMeasurer(
		//Utils.LineBreakMeasurer lineMeasurer = new Utils.LineBreakMeasurer(
			it,
			//new java.awt.font.FontRenderContext(null, false, false)
			// ######dette er suspekt. mÃ¥ heller skaffe en FontRenderContext
			// ved Ã¥ bruke getFontRenderContext() pÃ¥ et Graphics2D-objekt
			g.getFontRenderContext()
		);
		lineMeasurer.setPosition(itStart);

		//FontMetrics fontMetrics = new FontMetrics(font);   // oystein. ###abstract
		//int lineHeight = fontMetrics.getHeight();   // oystein

		// calculate number of lines and full layout height
		int lines = 0;
		int layHeight = 0;
		//float layWidth = 0;   // ###trenger ikke denne
		java.awt.font.TextLayout layout;
		while(lineMeasurer.getPosition() < itEnd) {

			layout = lineMeasurer.nextLayout(width);
			lines++;
			//System.out.println("\nlayout=" + layout);   // 2006-09-15
			//System.out.println("Descent=" + layout.getDescent());
			//System.out.println("Leading=" + layout.getLeading());
			//System.out.println("Ascent=" + layout.getAscent());
			// did a test and got
			// Descent=2.2719727
			// Leading=0.0
			// Ascent=11.005371
			// which yields a total of 13.277...
			// 14 pixels is correct.
			// ): needs to round upwards (i.e, ceiling). #####but what? total? or each contribution?
			//layHeight += layout.getDescent() + layout.getLeading() + layout.getAscent();   // ###fÃ¥r liksom 1 for lite
			layHeight += Math.ceil(layout.getDescent() + layout.getLeading() + layout.getAscent());
			//System.out.println("layHeight=" + layHeight);
			//layHeight += lineHeight;
			//float advance;
			//advance = layout.getVisibleAdvance();
			//if(layWidth < advance) {
			//	layWidth = advance;
			//}

		}

		if (lines > 0) {
			layHeight += 3;   // oystein ##############################
		}

		//System.out.println("final layHeight=" + layHeight);

		return layHeight;

	}

}

