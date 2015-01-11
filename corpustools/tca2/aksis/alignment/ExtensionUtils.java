/*
 * ExtensionUtils.java
 *
 * ...
 * ...
 * ...
 */

package aksis.alignment;

class ExtensionUtils {

	// <http://mindprod.com/jgloss/file.html>
	// There are no tools to look for an extension.
	// You have to do that yourself with code like this:
	public static String getExtension(String fileName) {

		String extension = "";
		int whereDot = fileName.lastIndexOf('.');
		if (0 < whereDot && whereDot <= fileName.length()-2) {
			extension = fileName.substring(whereDot+1);
		} else {
			extension = "";
		}
		return extension;

	}

	public static String getFilenameWithoutExtension(String fileName) {

		String fileNameWithoutExtension = "";
		int whereDot = fileName.lastIndexOf('.');
		if (0 < whereDot && whereDot <= fileName.length()-2) {
			fileNameWithoutExtension = fileName.substring(0, whereDot);
		} else {
			fileNameWithoutExtension = fileName;
		}
		return fileNameWithoutExtension;

	}

	public static String appendName(String fileName, String suffix) {

		return getFilenameWithoutExtension(fileName) + suffix + "." + getExtension(fileName);

	}

	public static String changeExtension(String fileName, String newExtension) {

		return getFilenameWithoutExtension(fileName) + "." + newExtension;

	}

}
