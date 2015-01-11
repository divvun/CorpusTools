/*
 * ErrorMessage.java
 *
 * ...
 * ...
 * ...
 */

package aksis.alignment;

import javax.swing.JOptionPane;

class ErrorMessage {

	public static void programError(String message) {
		System.err.println("*** Program error ***\n" + message);
		JOptionPane.showMessageDialog(
			null,
			message,
			"*** Program error ***",
			JOptionPane.WARNING_MESSAGE
		);
	}

	public static void error(String message) {
		System.err.println("*** Error ***\n" + message);
		JOptionPane.showMessageDialog(
			null,
			message,
			"*** Error ***",
			JOptionPane.WARNING_MESSAGE
		);
	}

}