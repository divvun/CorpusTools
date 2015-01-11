/*
 * MyExceptions.java
 *
 * ...
 * ...
 * @author Oystein Reigem
 */

package aksis.alignment;

class MyException extends Exception {}   // used in AlignGui.java

class EndOfAllTextsException extends Exception {}
class EndOfTextException extends Exception {}
class BlockedException extends Exception {}
//###hvordan? class EmptyElementException(String message) extends Exception(String message) {}   // 2006-09-19

class AncestorInfoRadioException extends Exception {}   // 2006-09-21. used in Settings.java

// ### dummy
class MyExceptions {}