/*
 * AlignGui.java
 *
 * ...
 * ...
 * ...
 */

package aksis.alignment;

import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.util.*;
import javax.swing.*;
import javax.swing.text.*;
import java.awt.geom.*;
import java.awt.font.*;
import org.w3c.dom.*;
import java.applet.AudioClip;
import java.nio.charset.*;
import java.util.regex.*;


/**
 *
 * @author Oystein Reigem and Johan Utne Poppe
 */

class AlignGui extends JPanel {

    // basic layout is
    //                     FIRST_COL = 0    DO_COL = 1    SECOND_COL = 2
    //                   +---------------+---------------+---------------+
    //                   |  <file_1>     |  <options>    |  <file_2>     |
    // FILE_ROW = 0      |  open/save    |  options      |  open/save    |
    //                   |  buttons      |               |  buttons      |
    //                   +---------------+---------------+---------------+
    //                   |  <aligned_1>  |  <unalign>    |  <aligned_2>  |
    // ALIGNED_ROW = 1   |  aligned      |  unalign      |  aligned      |
    //                   |  elements     |  button       |  elements     |
    //                   +---------------+---------------+---------------+
    //                   |  <work_1>     |  <do>         |  <work_2>     |
    // WORK_ROW = 2      |  elements     |  align & edit |  elements     |
    //                   |  under work   |  buttons      |  under work   |
    //                   +---------------+---------------+---------------+
    //                   |  <change_1>   |               |  <change_2>   |
    // CHANGE_ROW = 3    |  more/less    |               |  more/less    |
    //                   |  buttons      |               |  buttons      |
    //                   +---------------+---------------+---------------+
    //                   |  <unaligned_1>|  <batch>      |  <unaligned_2>|
    // UNALIGNED_ROW = 4 |  unaligned    |  batch align  |  unaligned    |
    //                   |  elements     |  button       |  elements     |
    //                   +---------------+---------------+---------------+
    // STATUS_ROW = 5    |  status line                                  |
    //                   +-----------------------------------------------+
    // (layout is gridbag not so much because we have merged cells but because we need cells of varying sizes)

    public static final int FIRST_COL = 0;
    public static final int DO_COL = 1;
    public static final int SECOND_COL = 2;
    public static final int THIRD_COL = 3;   // not used

    //public static final int TEXT_COL_WEIGHT = 1;
    public static final int TEXT_COL_WEIGHT = 2;
    public static final int DO_COL_WEIGHT = 0;
    
    public static final int FILE_ROW = 0;
    public static final int ALIGNED_ROW = 1;
    public static final int WORK_ROW = 2;
    public static final int CHANGE_ROW = 3;
    public static final int UNALIGNED_ROW = 4;
    public static final int STATUS_ROW = 5;
    public static final int FILE_ROW_WEIGHT = 0;
    public static final int ALIGNED_ROW_WEIGHT = 2;
    public static final int WORK_ROW_WEIGHT = 0;
    public static final int CHANGE_ROW_WEIGHT = 0;
    public static final int UNALIGNED_ROW_WEIGHT = 5;
    public static final int STATUS_ROW_WEIGHT = 0;

    public static final int MIN_DO_WIDTH = 200;
    public static final int MIN_WORK_HEIGHT = 200;

    public static final int[] TEXT_COLS = { FIRST_COL, SECOND_COL, THIRD_COL };   // THIRD_COL not used

	private JButton openFileButton[];
	private JButton saveAllFileButton;
	private JButton purgeButton;
	protected JPanel savePurgePanel;
	private JLabel filenameLabel[];
	private JFileChooser chooser;

	//options ¤¤¤
	private JButton anchorFileButton;
	private JLabel anchorFilenameLabel;
	private JLabel settingsFilenameLabel;   // 2006-09-21

	JList alignedListBox[];   // package access
	JScrollPane alignedScrollPane[];   // package access
	
	private JButton unalignButton;
	
	JList toAlignListBox[];   // package access
	JScrollPane toAlignScrollPane[];   // package access
	
	protected JLabel runLimitLabel1;
	protected JLabel runLimitLabel2;
	protected JTextField runLimitTextField;
	protected JPanel runPanel;
	protected ModeRadioButtonPanel modeRadioButtonPanel;
	protected JPanel settingsPanel;
	protected JPanel logPanel;
	protected JPanel skipPanel;
	protected JPanel breakPanel;
	protected JButton alignButton;
	private JButton settingsButton;   // brings up dialog for various settings
	private JButton startLoggingButton;
	private JButton stopLoggingButton;
	private JButton breakButton;   // 2006-08-15
	private JLabel logFilenameLabel;
	private JButton skipButton;   // button for use when opening half-aligned files. to skip the already aligned beginning of the files
	protected CompareInfo compareInfoPanel;
	private JScrollPane compareInfoScrollPane;
	protected Graphics compareInfoGraphics;
	protected JList matchInfoList;
	private JScrollPane matchInfoScrollPane;
	
	private JButton moreButton[];
	private JButton lessButton[];
	JList unalignedListBox[];   // package access
	JScrollPane unalignedScrollPane[];   // package access

	private JButton suggestButton;

	protected AlignStatusLine statusLine;

	// arrays of all the components lying in the same row.
	// for resizing of rows
	protected Component[] row2, row3, row5;
	protected double row2weighty, row5weighty;

	JMenuBar menuBar;   // package access

    protected OpenAction[]
    	openActions;
    protected SaveAllAction
    	saveAllAction;
    protected PurgeAction
    	purgeAction;
    protected AnchorAction
    	anchorAction;
    protected UnalignAction
    	unalignAction;
    protected AlignAction
    	alignAction;
    protected SettingsAction
    	settingsAction;
    protected StartLoggingAction
    	startLoggingAction;
    protected StopLoggingAction
    	stopLoggingAction;
    protected SkipCorrespAction
    	skipCorrespAction;
    protected BreakAction   // 2006-08-15
    	breakAction;
    protected MoreAction[]
    	moreActions;
    protected LessAction[]
    	lessActions;
    protected SuggestAction
    	suggestAction;
    protected HelpAction
    	helpAction;   // ¤¤¤
    protected ToolTipAction
    	toolTipAction;   // ¤¤¤

    AlignmentModel model;    // package access

    GridBagLayout layout;    // package access

    private AnchorDialog anchorDialog;

    private SettingsDialog settingsDialog;

	// <http://java.sun.com/developer/technicalArticles/InnerWorkings/customjlist/>
	//
	// Here's an example of a class that models the items in a list.
	// The class encapsulates the background color and text.
	//
	// ... -> AElement
	// String -> Object

	// forts.
	//
	// Here's an example of a class that implements the ListCellRenderer interface.
	//
	// Notice a few things about MyCellRenderer:
	//
	// It extends JLabel, another JFC Project Swing component.
	// JLabel is used to display text or images.
	// Extending JLabel is a convenient way to display selectable text or images.
	//
	// It sets opaque to true in the constructor.
	// This instructs the paint system to use the background of that particular component.
	//
	// It implements getListCellRendererComponent,
	// the only method in the ListCellRenderer interface.
	// This method sets the attributes of the class
	// and then returns a reference to the class.
	//
	// The setText method uses the string value stored
	// in the AElement object to set the JLabel text,
	// and the setBackground method uses the color value stored
	// in the AElement object to set the background color of the JLabel.
	//
	// If the list item is selected, that is the iss parameter
	// of getListCellRendererComponent is true,
	// MyCellRenderer uses the setBorder method to set
	// a two-pixel blue border around the list item.
	// The border around the item signals that the item is selected
	//
	// ... -> AElement
	// etc
	//
	// The customization possibilities don't end here.
	// By having the MyCellRenderer class extend a component other than JLabel,
	// you can create a wide variety of visually engaging lists.

	class MyCellRenderer extends JTextArea implements ListCellRenderer {   // ===
		public MyCellRenderer () {
			// Don't paint behind the component
			setOpaque(true);
		}

		// Set the attributes of the
		// class and return a reference
		public Component getListCellRendererComponent(
			JList list,
			Object value, // value to display
			int index,    // cell index
			boolean iss,  // is selected
			boolean chf)  // cell has focus?
		{

			setSize(1, 0);
			String text = ((AElement)(value)).toString();
			setText(text);   // if extends JTextArea
			setBackground(((AElement)(value)).getColor());
			setLineWrap(true);   // if extends JTextArea
			setWrapStyleWord(true);   // if extends JTextArea
			////System.out.println("getRows()=" + getRows());
			if (iss) {
				setBorder(BorderFactory.createLineBorder(Color.blue, 1));   // 1 = width of border in pixels
			} else {
				setBorder(BorderFactory.createLineBorder(list.getBackground(), 1));   // 1 = width of border in pixels
			}

			setFont(list.getFont());
			Graphics2D gg = (Graphics2D)getGraphics();
			if (gg != null) {
				setSize(new Dimension(list.getWidth() - 30, 0));   // 2006-09-19
				Font font = gg.getFont();
				}
			return this;
		}
	}

	/** Returns an ImageIcon, or null if the path was invalid. */
	protected static ImageIcon createImageIcon(String path, String description) {
		java.net.URL imgURL = AlignGui.class.getResource(path);
		if (imgURL != null) {
			return new ImageIcon(imgURL, description);
		} else {
			return null;
		}
	}

	private int getWhich(String command) throws MyException {
        for (int t=0; t<Alignment.NUM_FILES; t++) {
			if (command.indexOf(Integer.toString(t+1)) != -1) {
				return t;   // the action command contains the number ... . assume the command is about file ... ¤¤¤
			}
		}
		throw new MyException();
	}

    public static JFrame getTopJFrame(Component c) {
        while (!(c instanceof JFrame) && c != null) {
            c = c.getParent();
        }
        return (JFrame)c;
    }

	// create the menu bar
	private JMenuBar createMenu(OpenAction[] openActions,
	                            SaveAllAction saveAllAction,
	                            PurgeAction purgeAction,
	                            UnalignAction unalignAction,
	                            AnchorAction anchorAction,
	                            AlignAction alignAction,
	                            SettingsAction settingsAction,
	                            StartLoggingAction startLoggingAction,
	                            StopLoggingAction stopLoggingAction,
	                            SkipCorrespAction skipCorrespAction,
	                            BreakAction breakAction,
	                            MoreAction[] moreActions,
	                            LessAction[] lessActions,
	                            SuggestAction suggestAction,
	                            HelpAction helpAction,
	                            ToolTipAction toolTipAction) {

		JMenuBar mb = new JMenuBar();

		JMenu file = new JMenu("File");
		mb.add(file);
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			file.add(openActions[t]);
		}
		file.add(saveAllAction);
		file.add(purgeAction);

		JMenu edit = new JMenu("Edit");
		mb.add(edit);
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			edit.add(moreActions[t]);
			edit.add(lessActions[t]);
		}
		edit.add(unalignAction);
		edit.add(alignAction);
		edit.add(suggestAction);

		JMenu help = new JMenu("Help");
		mb.add(help);
		help.add(helpAction);
		JCheckBoxMenuItem menuItem = new JCheckBoxMenuItem(toolTipAction);
		help.add(menuItem);
		ToolTipManager.sharedInstance().setEnabled(false);
		menuItem.setState(false);

		return mb;

	}

	public AudioClip sound;   // ################

	public abstract class MyAbstractAction extends AbstractAction {
		public MyAbstractAction(String text, ImageIcon icon, String desc, KeyStroke accelerator, Integer mnemonic) {
			super(text, icon);
			putValue(SHORT_DESCRIPTION, desc);
			putValue(ACCELERATOR_KEY, accelerator);
			putValue(MNEMONIC_KEY, mnemonic);   // alt+...
		}
	}

	public class OpenAction extends MyAbstractAction {
		public OpenAction(String text, ImageIcon icon, String desc, KeyStroke accelerator, Integer mnemonic) {
			super(text, icon, desc, accelerator, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {
			AlignGui.this.statusLine.clear();
			int t;
			String command = e.getActionCommand();
			// the command contains a '1' or '2'
			// t is 0 or 1 and tells if this action regards file 1 or file 2
			try {
				t = getWhich(command);
			} catch (MyException ex) {
				ErrorMessage.programError("Can't determine which file to open. command is '" + command + "'");   // 2006-08-10
				return;
			}

			// check if a file has already been read in
			if (model.docs[t] == null) {
				chooser = new JFileChooser();
				chooser.setApproveButtonText("Open file " + (t+1));
				if (model.currentOpenDirectory != null) {
					chooser.setCurrentDirectory(model.currentOpenDirectory);
				} else {
					chooser.setCurrentDirectory(null);
				}
				int returnVal = chooser.showOpenDialog(AlignGui.this);
				if(returnVal == JFileChooser.APPROVE_OPTION) {
			        try {   // 2006-09-19
			            model.loadFile(AlignGui.this, chooser.getSelectedFile(), t);
					} catch (Exception ex2) {
						ErrorMessage.error("Error. The text contains an empty alignable element:\n\n" + ex2.getMessage() + "\n\n\n(Note that the element might be differently formatted in the input file.\nAlso you might need to restart the program when this error occurs)");
					}

					filenameLabel[t].setText(chooser.getSelectedFile().getName());
					model.currentOpenDirectory = chooser.getCurrentDirectory();
				}

			} else {

				// ¤¤¤ should be a message here too
				Toolkit.getDefaultToolkit().beep();
				System.out.println("Can't read in new file. Not implemented");

			}

		}
	}

	public class SaveAllAction extends MyAbstractAction {
		public SaveAllAction(String text, ImageIcon icon, String desc, KeyStroke accelerator, Integer mnemonic) {
			super(text, icon, desc, accelerator, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {
			AlignGui.this.statusLine.clear();

			// establish corresp attributes in dom for all texts.
			// methods for saving in "corresp" and "external" formats depend on this
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				AlignGui.this.model.setCorrespAttributes(t);
			}

			File tempPath;
			String outputFilenameSuggestion;
			File outputFilepathSuggestion;
			int returnVal;

			// save in "external" format
			// the basis for the suggestion is the input file paths
			outputFilenameSuggestion = "";
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				tempPath = new File(AlignGui.this.model.inputFilepath[t]);
				String tempFilename = tempPath.getName();
				if (outputFilenameSuggestion != "") {
					outputFilenameSuggestion += "_";
				}
				outputFilenameSuggestion += ExtensionUtils.getFilenameWithoutExtension(tempFilename);
			}
			outputFilenameSuggestion += ".xml";

			outputFilepathSuggestion = new File(chooser.getCurrentDirectory(), outputFilenameSuggestion);

			chooser.setSelectedFile(outputFilepathSuggestion);
			returnVal = chooser.showSaveDialog(AlignGui.this);
			if (returnVal == JFileChooser.APPROVE_OPTION) {
				// save in "external" format
				AlignGui.this.model.saveExternalFormatFile(chooser.getSelectedFile());
				model.currentSaveDirectory = chooser.getCurrentDirectory();
			}

			for (int t=0; t<Alignment.NUM_FILES; t++) {

				// the basis for the suggestion is the input file path
				tempPath = new File(AlignGui.this.model.inputFilepath[t]);
				String tempFilename = tempPath.getName();

				for (int fi=0; fi<2; fi++) {

					chooser = new JFileChooser();

					String approveButtonText = "Save file " + (t+1);
					if (fi == 0) {
						// save in corresp format
						approveButtonText += " in corresp format";
					//} else {
					} else if (fi == 1) {
						// save in newline format
						approveButtonText += " in newline format";
					} else {
						// save in "external" format. 2006-11-20 ###nei, det har vi vel flyttet lenger opp
						approveButtonText += " in 'external' format";
					}
					chooser.setApproveButtonText(approveButtonText);
					if (model.currentSaveDirectory != null) {
						chooser.setCurrentDirectory(model.currentSaveDirectory);
					} else if (model.currentOpenDirectory != null) {
						chooser.setCurrentDirectory(model.currentOpenDirectory);
					} else {
						chooser.setCurrentDirectory(null);
					}

					if (fi == 0) {
							outputFilenameSuggestion = ExtensionUtils.appendName(tempFilename, "_cor");
					} else {
						// save in newline format
						outputFilenameSuggestion = ExtensionUtils.changeExtension(ExtensionUtils.appendName(tempFilename, "_new"), "txt");   // ### ¤¤¤ ###########
					}

					// the suggestion must obey the current directory for saving files
					outputFilepathSuggestion = new File(chooser.getCurrentDirectory(), outputFilenameSuggestion);

					// dialog
					chooser.setSelectedFile(outputFilepathSuggestion);
					returnVal = chooser.showSaveDialog(AlignGui.this);
					if (returnVal == JFileChooser.APPROVE_OPTION) {
						if (fi == 0) {
							// save in corresp format
							AlignGui.this.model.saveCorrespFormatFile(chooser.getSelectedFile(), t, AlignGui.this.model.getCharset(t));
						} else {
							// save in newline format
							AlignGui.this.model.saveNewlineFormatFile(chooser.getSelectedFile(), t, AlignGui.this.model.getCharset(t), AlignGui.this.model.getAncestorFilter());
						}
						model.currentSaveDirectory = chooser.getCurrentDirectory();
					}
				}
			}
		}
	}

	public class PurgeAction extends MyAbstractAction {

		public PurgeAction(String text, ImageIcon icon, String desc, KeyStroke accelerator, Integer mnemonic) {
			super(text, icon, desc, accelerator, mnemonic);
		}
		public void actionPerformed(ActionEvent e){
			AlignGui.this.statusLine.clear();
			AlignGui.this.model.purge(AlignGui.this);
		}
	}

	public class AnchorAction extends MyAbstractAction {
		public AnchorAction(String text, ImageIcon icon, String desc, KeyStroke accelerator, Integer mnemonic) {
			super(text, icon, desc, accelerator, mnemonic);
		}
		public void actionPerformed(ActionEvent e){
			AlignGui.this.statusLine.clear();
			anchorDialog = new AnchorDialog(null, AlignGui.this, -1);
			anchorDialog.setLocationRelativeTo(AlignGui.this);
			anchorDialog.setVisible(true);
			if (anchorDialog.approved) {
				AlignGui.this.model.compare = new Compare();
			}

		}
	}

	public class MoreAction extends MyAbstractAction {
		public MoreAction(String text, ImageIcon icon, String desc, KeyStroke accelerator, Integer mnemonic) {
			super(text, icon, desc, accelerator, mnemonic);
		}
		public void actionPerformed(ActionEvent e){
			AlignGui.this.statusLine.clear();

			int t;
			String command = e.getActionCommand();
			// the command contains a '1' or '2'
			// t is 0 or 1 and tells if this action regards file 1 or file 2
			try {
				t = getWhich(command);
			} catch (MyException ex) {
				//System.err.println("command is '" + command + "'");
				ErrorMessage.programError("Can't determine which text you're working on. command is '" + command + "'");   // 2006-08-10
				return;
			}
			model.toAlign.pickUp(t, model.unaligned.pop(t));
			model.updateGuiAfterMore(AlignGui.this);
		}
	}

	public class LessAction extends MyAbstractAction {
		public LessAction(String text, ImageIcon icon, String desc, KeyStroke accelerator, Integer mnemonic) {
			super(text, icon, desc, accelerator, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {
			AlignGui.this.statusLine.clear();

			int t;
			String command = e.getActionCommand();
			// the command contains a '1' or '2'
			// t is 0 or 1 and tells if this action regards file 1 or file 2
			try {
				t = getWhich(command);
			} catch (MyException ex) {
				ErrorMessage.programError("Can't determine which text you're working on. command is '" + command + "'");   // 2006-08-10
				return;
			}
			model.less(AlignGui.this, t);
		}
	}

	public class AlignAction extends MyAbstractAction {
		public AlignAction(String text, ImageIcon icon, String desc, KeyStroke accelerator, Integer mnemonic) {
			super(text, icon, desc, accelerator, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {
			AlignGui.this.statusLine.clear();
			model.align(AlignGui.this, true);   // true = scroll aligned
		}
	}

	public class UnalignAction extends MyAbstractAction {
		public UnalignAction(String text, ImageIcon icon, String desc, KeyStroke accelerator, Integer mnemonic) {
			super(text, icon, desc, accelerator, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {
			AlignGui.this.statusLine.clear();
			model.unalign(AlignGui.this);
		}
	}

	public class SettingsAction extends MyAbstractAction {
		public SettingsAction(String text, ImageIcon icon, String desc, KeyStroke accelerator, Integer mnemonic) {
			super(text, icon, desc, accelerator, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {
			AlignGui.this.statusLine.clear();

			settingsDialog = new SettingsDialog(null, AlignGui.this);   // 2006-09-21
			settingsDialog.setLocationRelativeTo(AlignGui.this);
			settingsDialog.setVisible(true);
			if (settingsDialog.approved) {
				AlignGui.this.model.compare = new Compare();
			}

		}
	}

	public class StartLoggingAction extends MyAbstractAction {

		public StartLoggingAction(String text, ImageIcon icon, String desc, KeyStroke accelerator, Integer mnemonic) {
			super(text, icon, desc, accelerator, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {
			AlignGui.this.statusLine.clear();

			if (model.logFileOut == null) {

				String logFilenameSuggestion = "";
				for (int t=0; t<Alignment.NUM_FILES; t++) {
					String tempFilename;
					// find name of input file t - just the file name - no path, no extension
					if (AlignGui.this.model.inputFilepath[t] != null) {
						File tempPath = new File(AlignGui.this.model.inputFilepath[t]);
						tempFilename = tempPath.getName();
						tempFilename = ExtensionUtils.getFilenameWithoutExtension(tempFilename);
					} else {
						// no inputfile. use a number (1, 2) as a surrogate
						tempFilename = "" + (t+1);   // ######
					}
					// but the suggestion must obey the current directory for saving files,
					// so we need just the file names, without the extension.
					// we string them together with an underscore between them
					if (logFilenameSuggestion == "") {
						logFilenameSuggestion += "log_";
					} else {
						logFilenameSuggestion += "_";
					}
					logFilenameSuggestion += tempFilename;
				}
				// finally add extension
				logFilenameSuggestion += ".txt";

				chooser = new JFileChooser();
				chooser.setApproveButtonText("Save log file");  // ###
				if (model.currentSaveDirectory != null) {
					chooser.setCurrentDirectory(model.currentSaveDirectory);
				} else {
					if (model.currentOpenDirectory != null) {
						chooser.setCurrentDirectory(model.currentOpenDirectory);
					} else {
						chooser.setCurrentDirectory(null);
					}
				}

				// the suggestion must obey the current directory for ...
				File logFilepathSuggestion = new File(chooser.getCurrentDirectory(), logFilenameSuggestion);

				// dialog
				chooser.setSelectedFile(logFilepathSuggestion);
				int returnVal = chooser.showSaveDialog(AlignGui.this);   // vil helst ha en fornuftig parent, men
				if (returnVal == JFileChooser.APPROVE_OPTION) {

					File f = chooser.getSelectedFile();

					try {

						OutputStream fOut = new FileOutputStream(f);
						OutputStream bOut = new BufferedOutputStream(fOut);
						Charset cs = Charset.forName("UTF-8");
						model.logFileOut = new OutputStreamWriter(bOut, cs);

					} catch (Exception ex) {

						// ¤¤¤ PLAIN_MESSAGE, INFORMATION_MESSAGE, WARNING_MESSAGE, ERROR_MESSAGE?
						//¤¤¤ advarselsdialog her eller i kallende kode?
						JOptionPane.showMessageDialog(
							null,
							"Can't open log file " + f.getName(),
							"¤¤¤Title",
							JOptionPane.ERROR_MESSAGE
						);
						ErrorMessage.error("Exception when opening " + model.getLogFilename() + ":\n" + ex.toString());   // 2006-08-10
						//ex.printStackTrace();

					}

					model.setLogging(true);
					model.setLogFilename(f.getName());
					AlignGui.this.setLogFilenameLabel(f.getName());

					startLoggingButton.setVisible(!model.getLogging());
					stopLoggingButton.setVisible(model.getLogging());

					try {
						String text = ">>> Logging started <<<\n\n";   // 2006-04-18
						model.logFileOut.write(text, 0, text.length());
					} catch (Exception ex) {
						ErrorMessage.error("Exception when writing to " + model.getLogFilename() + ":\n" + ex.toString());   // 2006-08-10
						//ex.printStackTrace();
					}

				}

			} else {

				model.setLogging(true);
				startLoggingButton.setVisible(!model.getLogging());
				stopLoggingButton.setVisible(model.getLogging());

				try {
					String text = ">>> Logging restarted <<<\n\n";   // 2006-04-18
					model.logFileOut.write(text, 0, text.length());
				} catch (Exception ex) {
					ErrorMessage.error("Exception when writing to " + model.getLogFilename() + ":\n" + ex.toString());   // 2006-08-10
					//ex.printStackTrace();
				}

			}

		}
	}

	public class StopLoggingAction extends MyAbstractAction {

		public StopLoggingAction(String text, ImageIcon icon, String desc, KeyStroke accelerator, Integer mnemonic) {
			super(text, icon, desc, accelerator, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {
			AlignGui.this.statusLine.clear();

			try {
				String text = ">>> Logging stopped <<<\n\n";   // 2006-04-18
				model.logFileOut.write(text, 0, text.length());
			} catch (Exception ex) {
				ErrorMessage.error("Exception when writing to " + model.getLogFilename() + ":\n" + ex.toString());   // 2006-08-10
				//ex.printStackTrace();
			}

			model.setLogging(false);
			startLoggingButton.setVisible(!model.getLogging());
			stopLoggingButton.setVisible(model.getLogging());

		}
	}

	public class SkipCorrespAction extends MyAbstractAction {
		public SkipCorrespAction(String text, ImageIcon icon, String desc, KeyStroke accelerator, Integer mnemonic) {
			super(text, icon, desc, accelerator, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {
			AlignGui.this.statusLine.clear();

			model.skipCorresp(AlignGui.this);
		}
	}

	// 2006-08-15
	public class BreakAction extends MyAbstractAction {
		public BreakAction(String text, ImageIcon icon, String desc, KeyStroke accelerator, Integer mnemonic) {
			super(text, icon, desc, accelerator, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {
			AlignGui.this.statusLine.clear();

			model.break_(AlignGui.this);
		}
	}

	public class SuggestAction extends MyAbstractAction {
		public SuggestAction(String text, ImageIcon icon, String desc, KeyStroke accelerator, Integer mnemonic) {
			super(text, icon, desc, accelerator, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {
			AlignGui.this.statusLine.clear();

			model.suggest(AlignGui.this);

		}
	}

	public class HelpAction extends MyAbstractAction {
		public HelpAction(String text, ImageIcon icon, String desc, KeyStroke accelerator, Integer mnemonic) {
			super(text, icon, desc, accelerator, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {

			AlignGui.this.statusLine.clear();

			JOptionPane.showMessageDialog(null, "Help - not implemented.\n\nProgram version: " + Alignment.VERSION, "Not implemented", JOptionPane.INFORMATION_MESSAGE);   // 2006-09-19

		}
	}

	// ... toolTipAction
	public class ToolTipAction extends MyAbstractAction {
		public ToolTipAction(String text, ImageIcon icon, String desc, KeyStroke accelerator, Integer mnemonic) {
			super(text, icon, desc, accelerator, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {
			AlignGui.this.statusLine.clear();

			// <http://javaalmanac.com/egs/javax.swing/tooltip_EnableTt.html>
			if (ToolTipManager.sharedInstance().isEnabled()) {
				// enable tool tips for the entire application
				ToolTipManager.sharedInstance().setEnabled(false);
			} else {
				// disable tool tips for the entire application
				ToolTipManager.sharedInstance().setEnabled(true);
			}

		}
	}

	public int getMode() {
		int mnemonic = AlignGui.this.modeRadioButtonPanel.rbg.getSelection().getMnemonic();
		if (mnemonic == KeyEvent.VK_O) {
			return Alignment.MODE_ONE;
		} else if (mnemonic == KeyEvent.VK_S) {
			return Alignment.MODE_SKIP11;
		} else if (mnemonic == KeyEvent.VK_A) {
			return Alignment.MODE_AUTO;
		} else {
			// ##### program error ####
			return Alignment.MODE_ONE;
		}
	}

	public void setAnchorFilenameLabel(String fileName) {
		anchorFilenameLabel.setText(fileName);
	}

	// 2006-09-21
	public void setSettingsFilenameLabel(String fileName) {
		settingsFilenameLabel.setText(fileName);
	}
	// end 2006-09-21

	public void setLogFilenameLabel(String fileName) {
		logFilenameLabel.setText(fileName);
	}

    AlignGui(AlignmentModel model) {

		// 2008-08-27
		// <http://www.iam.ubc.ca/guides/javatut99/uiswing/misc/plaf.html>:
		// "To specify the Java Look & Feel,
		// we used the getCrossPlatformLookAndFeelClassName method.
		// If you want to specify the native look and feel
		// for whatever platform the user runs the program on,
		// use getSystemLookAndFeelClassName, instead."

		String plafClassName =
			 UIManager.getSystemLookAndFeelClassName();   // 2008-08-27
		try {
			UIManager.setLookAndFeel(plafClassName);
		} catch(Exception ex) {
			System.out.println(ex);
		}
		SwingUtilities.updateComponentTreeUI(this);

		this.model = model;

		String key;   // 2006-08-15

		OpenAction[] openActions = new OpenAction[Alignment.NUM_FILES];
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			//System.out.println(t);
			// 2006-08-15
			if (t == 0) {
				key = "control O";
			} else {
				key = "shift control O";
			}
			openActions[t] = new
				OpenAction(
					"Open file " + (t+1),
					createImageIcon("images/Read.gif", "read from disc"),
					"Open file " + (t+1),
					//null,
					KeyStroke.getKeyStroke(key),   // 2006-08-15 #######
					new Integer(0)
				);
		}

		SaveAllAction saveAllAction = new
			SaveAllAction(
				//"Save all files",
				"Save result",
				createImageIcon("images/Write.gif", "write to disc"),
				"Save result",
				//null,
				KeyStroke.getKeyStroke("control S"),   // 2006-08-15
				new Integer(0)
			);

		PurgeAction purgeAction = new
			PurgeAction(
				"Clear all data",
				createImageIcon("images/Purge.gif", "clear all data"),
				"Clear all data",
				//null,
				KeyStroke.getKeyStroke("control X"),   // 2006-08-15 #########X
				new Integer(0)
			);

		AnchorAction anchorAction = new
			AnchorAction(
				"Anchor words",
				createImageIcon("images/Anchor.gif", "anchor"),
				"Unalign",
				null,
				new Integer(0)
			);

		UnalignAction unalignAction = new
			UnalignAction(
				"Unalign",
				createImageIcon("images/Down.gif", "arrow down"),
				"Unalign",
				KeyStroke.getKeyStroke("pressed DOWN"),
				new Integer(0)
			);

		AlignAction alignAction = new
			AlignAction(
				//"Align",
				"Accept",   // 2006-12-19
				createImageIcon("images/Up.gif", "arrow up"),
				//"Align",
				"Accept",   // 2006-12-19
				//null,
				KeyStroke.getKeyStroke("control UP"),   // 2006-08-15 ######
				new Integer(0)
			);

		SettingsAction settingsAction = new
			SettingsAction(
				"Settings",
				createImageIcon("images/Settings.gif", "dialog form"),
				"Settings",
				null,
				new Integer(0)
			);

		StartLoggingAction startLoggingAction = new
			StartLoggingAction(
				"Start logging",
				createImageIcon("images/Log.gif", "log"),
				"Start logging",
				null,
				new Integer(0)
			);

		StopLoggingAction stopLoggingAction = new
			StopLoggingAction(
				"Stop logging",
				createImageIcon("images/Log.gif", "log"),
				"Stop logging",
				null,
				new Integer(0)
			);

		SkipCorrespAction skipCorrespAction = new
			SkipCorrespAction(
				"Skip what's already aligned",
				createImageIcon("images/SkipAligned.gif", "aligned elements above unaligned ones, with arrow passing the aligned ones"),
				"Skip what's already aligned",
				null,
				new Integer(0)
			);

		BreakAction breakAction = new
			BreakAction(
				"Break",
				createImageIcon("images/Break.gif", "log"),
				"Break",
				KeyStroke.getKeyStroke("control C"),
				new Integer(0)
			);

		MoreAction[] moreActions = new MoreAction[Alignment.NUM_FILES];
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			if (t == 0) {
				key = "pressed LEFT";
			} else {
				key = "pressed RIGHT";
			}
			moreActions[t] = new
				MoreAction(
					//"More " + (t+1),
					"Up (text " + (t+1) + ")",
					createImageIcon("images/Up.gif", "arrow up"),
					//"More " + (t+1),
					"Up (text " + (t+1) + ")",
					//KeyStroke.getKeyStroke("typed j"),
					KeyStroke.getKeyStroke(key),
					new Integer(0)
				);
		}

		LessAction[] lessActions = new LessAction[Alignment.NUM_FILES];
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			if (t == 0) {
				key = "shift pressed LEFT";
			} else {
				key = "shift pressed RIGHT";
			}
			lessActions[t] = new
				LessAction(
					//"Less " + (t+1),
					"Down (text " + (t+1) + ")",
					createImageIcon("images/Down.gif", "arrow down"),
					//"Less " + (t+1),
					"Down (text " + (t+1) + ")",
					//KeyStroke.getKeyStroke("typed k"),
					KeyStroke.getKeyStroke(key),
					new Integer(0)
				);
		}

		SuggestAction suggestAction = new
			SuggestAction(
				"Suggest",
				createImageIcon("images/Up.gif", "arrow up"),
				"Suggest",
				KeyStroke.getKeyStroke("pressed UP"),
				new Integer(0)
			);

		// help action

		HelpAction helpAction = new
			HelpAction(
				"Help",
				createImageIcon("images/Help.gif", "question mark"),
				"Help",
				KeyStroke.getKeyStroke("F1"),   // 2006-08-15
				new Integer(0)
			);

		ToolTipAction toolTipAction = new
			ToolTipAction(
				"ToolTip",
				createImageIcon("images/ToolTip.gif", "yellow tooltip rectangle"),
				"ToolTip",
				KeyStroke.getKeyStroke("control T"),   // 2006-08-15 ########T
				new Integer(0)
			);

		// colours

        // Marlén's colours
        Color bgColor = new Color(0xF5DEB3);   // #F5DEB3
        Color buttonColor = new Color(0x94BA45);   // #94BA45
        Color buttonTextColor = new Color(0x006400);   // #006400

        Font plainFont = this.getFont().deriveFont(Font.PLAIN);

		// create menu that uses the above actions

		menuBar =
			createMenu(
				openActions,
				saveAllAction,
				purgeAction,
				unalignAction,
				anchorAction,
				alignAction,
				settingsAction,
				startLoggingAction,
				stopLoggingAction,
				skipCorrespAction,
				breakAction,
				moreActions,
				lessActions,
				suggestAction,
				helpAction,
				toolTipAction
			);


        // gui objects
		openFileButton = new JButton[Alignment.NUM_FILES];
		filenameLabel = new JLabel[Alignment.NUM_FILES];
		saveAllFileButton = new JButton(saveAllAction);
		purgeButton = new JButton(purgeAction);
		savePurgePanel = new JPanel();

		anchorFileButton = new JButton(anchorAction);
		anchorFilenameLabel = new JLabel("");
		anchorFilenameLabel.setFont(anchorFilenameLabel.getFont().deriveFont(10.0f));

		settingsFilenameLabel = new JLabel("");   // 2006-09-21
		settingsFilenameLabel.setFont(settingsFilenameLabel.getFont().deriveFont(10.0f));   // 2006-09-21

        alignedListBox = new JList[Alignment.NUM_FILES];
        alignedScrollPane = new JScrollPane[Alignment.NUM_FILES];

		unalignButton = new JButton(unalignAction);

        toAlignListBox = new JList[Alignment.NUM_FILES];
        toAlignScrollPane = new JScrollPane[Alignment.NUM_FILES];

		runLimitLabel1 = new JLabel("Skip/auto limit:");
		runLimitTextField = new JTextField("999999");   // ########## for å få bredde på feltet
		runLimitTextField.setFont(plainFont);
		// select all when the fields gets focus
		runLimitTextField.addFocusListener(new FocusAdapter() {
			public void focusGained(FocusEvent e) {
				JTextField field = (JTextField)e.getSource();
				field.selectAll();
			}
		});
		runLimitLabel2 = new JLabel("alignments");
		runPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
		runPanel.setMaximumSize(new Dimension(300, 0));   // ###without this the panel gets wider than its content, resulting in indentation of the content

		modeRadioButtonPanel = new ModeRadioButtonPanel(bgColor, plainFont);
		modeRadioButtonPanel.setMaximumSize(new Dimension(300, 0));

		alignButton = new JButton(alignAction);
		settingsPanel = new JPanel(new FlowLayout(FlowLayout.CENTER));   // ### prøvde LEFT. ble da venstrejust, og det ville jeg ha, men det kom litt padding foran, og det ville jeg ikke ha. box + strut mellom de to knappene + glue på slutten hadde sikkert vært bedre. eller springlayout, som jeg aldri har prøvd. flow center er default og ikke nødvendig
		logPanel = new JPanel(new FlowLayout(FlowLayout.CENTER));
		skipPanel = new JPanel();
		breakPanel = new JPanel();   // 2006-08-15
		settingsPanel.setMaximumSize(new Dimension(300, 0));   // ###see runPanel
		settingsButton = new JButton(settingsAction);
		logPanel.setMaximumSize(new Dimension(300, 0));
		startLoggingButton = new JButton(startLoggingAction);
		stopLoggingButton = new JButton(stopLoggingAction);
		breakPanel.setMaximumSize(new Dimension(300, 0));   // 2006-08-15
		breakButton = new JButton(breakAction);   // 2006-08-15
		logFilenameLabel = new JLabel("");
		logFilenameLabel.setFont(logFilenameLabel.getFont().deriveFont(10.0f));
		skipPanel.setMaximumSize(new Dimension(300, 0));
		skipButton = new JButton(skipCorrespAction);

		compareInfoPanel = new CompareInfo();
		compareInfoPanel.setSize(1000, 1000);   // ###########
		compareInfoPanel.setPreferredSize(new Dimension (1000, 1000));   // ###########
		compareInfoPanel.setMinimumSize(new Dimension (1000, 1000));   // ###########
		compareInfoPanel.setGui(this);
		compareInfoScrollPane = new JScrollPane(compareInfoPanel);

		matchInfoList = new JList(this.model.matchInfo.displayableList);
		matchInfoScrollPane = new JScrollPane(matchInfoList);
		matchInfoList.setName("M");
		Font font = matchInfoList.getFont();
		matchInfoList.setFont(new Font(font.getName(), Font.PLAIN, font.getSize()));

		moreButton = new JButton[Alignment.NUM_FILES];
		lessButton = new JButton[Alignment.NUM_FILES];

        unalignedListBox = new JList[Alignment.NUM_FILES];
        unalignedScrollPane = new JScrollPane[Alignment.NUM_FILES];
		suggestButton = new JButton(suggestAction);

		statusLine = new AlignStatusLine();

        for (int t=0; t<Alignment.NUM_FILES; t++) {

			openFileButton[t] = new JButton(openActions[t]);
			openFileButton[t].setName("O" + t);
			filenameLabel[t] = new JLabel("");

	        alignedListBox[t] = new JList(this.model.aligned.elements[t]);
	        alignedListBox[t].setName("A" + t);
	        alignedListBox[t].setCellRenderer(new MyCellRenderer());   // ### MyCellRenderer burde vel hete ettellerannetelementsCellRenderer

			toAlignListBox[t] = new JList(this.model.toAlign.elements[t]);
	        toAlignListBox[t].setName("T" + t);   // mouse event handler needs a name, to be able to find out which list box was clicked
	        toAlignListBox[t].setCellRenderer(new MyCellRenderer());

			lessButton[t] = new JButton(lessActions[t]);
			moreButton[t] = new JButton(moreActions[t]);

	        unalignedListBox[t] = new JList(this.model.unaligned.elements[t]);
	        unalignedListBox[t].setName("U" + t);
	        unalignedListBox[t].setCellRenderer(new MyCellRenderer());
		}

		// handler for mouse events in toAlign

		// ¤¤¤ kan vi ha denne som en action?
		// ¤¤¤ er det mulig å gjøre dette uten mus?
		MouseListener toAlignMouseListener = new MouseAdapter() {

			public void mouseClicked(MouseEvent e) {

				Object[] options = { "Yes", "No" };   // button texts
				int n = JOptionPane.showOptionDialog(
					null,
					"Do you want to change the suggested alignment(s)",
					"Change alignment(s)",
					JOptionPane.YES_NO_OPTION,
					JOptionPane.QUESTION_MESSAGE,
					null,
					options,
					options[1]   // the choice that is initially selected
				);
				if(n == 0) {
					AlignGui.this.statusLine.clear();

					int tClicked = Integer.parseInt(e.getComponent().getName().substring(1, 2));
					int indexClicked = ((JList)(e.getComponent())).locationToIndex(e.getPoint());
					int elementNumberClicked = ((AElement)(AlignGui.this.model.toAlign.elements[tClicked].get(0))).elementNumber + indexClicked;
					int alignmentNumberClicked = ((AElement)(AlignGui.this.model.toAlign.elements[tClicked].get(indexClicked))).alignmentNumber;

					AlignGui.this.model.link(AlignGui.this, tClicked, indexClicked, elementNumberClicked, -2);  // being told to link to alignment number -2 is a signal to link to next available pending alignment
				}   // 2006-09-25
			}
		};
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			toAlignListBox[t].addMouseListener(toAlignMouseListener);
		}

		// handler for mouse events in aligned and unaligned.
		// synchronizes texts for the various languages

		// ¤¤¤ kan vi ha denne som en action?
		// ¤¤¤ er det mulig å gjøre dette uten mus?
		MouseListener alignedAndUnalignedMouseListener = new MouseAdapter() {

			public void mouseClicked(MouseEvent e) {
				AlignGui.this.statusLine.clear();

				String componentName = e.getComponent().getName();
				String aClicked = componentName.substring(0, 1);   // "A" for aligned, or "U" for unaligned
				int tClicked = Integer.parseInt(componentName.substring(1, 2));
				int indexClicked = ((JList)(e.getComponent())).locationToIndex(e.getPoint());

				if (aClicked.equals("A")) {

					// user clicked in aligned

					int elementNumberClicked = indexClicked;
					int alignmentNumberClicked = ((AElement)(AlignGui.this.model.aligned.elements[tClicked].get(indexClicked))).alignmentNumber;

					for (int t=0; t<Alignment.NUM_FILES; t++) {
						Link alignment = (Link)(AlignGui.this.model.aligned.alignments.get(alignmentNumberClicked));
						Set elementNumbers = alignment.getElementNumbers(t);
						if (elementNumbers.size() > 0) {
							// find smallest index of aligned element in other text
							int smallestIndex = Integer.MAX_VALUE;
							int highestIndex = Integer.MIN_VALUE;
							Iterator eIt = alignment.elementNumbers[t].iterator();
							while (eIt.hasNext()) {
								int elementNumber = ((Integer)(eIt.next())).intValue();
								if (elementNumber < smallestIndex) {
									smallestIndex = elementNumber;
								}
								if (elementNumber > highestIndex) {
									highestIndex = elementNumber;
								}
							}

							alignedListBox[t].ensureIndexIsVisible(highestIndex);
							alignedListBox[t].ensureIndexIsVisible(smallestIndex);
							alignedListBox[t].setSelectedIndex(smallestIndex);
						} else {
							Toolkit.getDefaultToolkit().beep();

						}
					}

				} else { // "U"

					// user clicked in unaligned

					int elementNumberClicked = ((AElement)(AlignGui.this.model.unaligned.elements[tClicked].get(0))).elementNumber + indexClicked;

					int numThis = unalignedListBox[tClicked].getModel().getSize();
					int numOther = -1;
					int otherIndex = -1;
					for (int t=0; t<Alignment.NUM_FILES; t++) {
						if (t != tClicked) {
							numOther = unalignedListBox[t].getModel().getSize();
							if (numOther > 0) {
								otherIndex =          Math.round(((((float)(indexClicked + 1) * numOther) - 1) / numThis) - 1);
								unalignedListBox[t].ensureIndexIsVisible(otherIndex);
								unalignedListBox[t].setSelectedIndex(otherIndex);
							}
						}
					}

				}

				// ...

			}

		};
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			alignedListBox[t].addMouseListener(alignedAndUnalignedMouseListener);
			unalignedListBox[t].addMouseListener(alignedAndUnalignedMouseListener);
		}

		// handler for mouse events in matchInfoList
		MouseListener matchInfoListMouseListener = new MouseAdapter() {

			public void mouseClicked(MouseEvent e) {
				AlignGui.this.statusLine.clear();

				int indexClicked = matchInfoList.locationToIndex(e.getPoint());
				if (indexClicked != -1) {
					String line = (String)AlignGui.this.model.matchInfo.displayableList.get(indexClicked);
					String w = line.trim().split(" ")[0];   // ######### grisete
					try {
						int n = Integer.parseInt(w) - 1;
						anchorDialog = new AnchorDialog(null, AlignGui.this, n);
						anchorDialog.setLocationRelativeTo(AlignGui.this);
						anchorDialog.setVisible(true);
						if (anchorDialog.approved) {
							AlignGui.this.model.compare = new Compare();
						}
					} catch (Exception ex) {
					}
				}
			}

		};
		matchInfoList.addMouseListener(matchInfoListMouseListener);

		// tool tip

		//saveAllFileButton.setToolTipText("Save texts");
		saveAllFileButton.setToolTipText("Save aligned result");
		purgeButton.setToolTipText("Claer all data from the system and make ready for new input files");
		anchorFileButton.setToolTipText("Select and/or edit anchor list");
		modeRadioButtonPanel.setToolTipText("Select between various modes ...blah blah...");
		unalignButton.setToolTipText("Drop latest alignment");
		alignButton.setToolTipText("Accept the pending alignment(s)");
		settingsButton.setToolTipText("Set various parameters");
		startLoggingButton.setToolTipText("Start logging");
		stopLoggingButton.setToolTipText("Stop logging");
		breakButton.setToolTipText("Break alignment process");   // 2006--08-15
		skipButton.setToolTipText("Skip already aligned elements (relevant when opening half-aligned texts)");
		runLimitTextField.setToolTipText("Limits the number of alignments done in Skip 1-1 and Automatic modes");
		suggestButton.setToolTipText("Suggest elements to align");
		compareInfoPanel.setToolTipText("<html>Indication of path forward.<br>Small squares show how well possible 1-1 alignments in the \"future\" match, with numbers and colours.<br>Similarly, small rectangles show the same information for possible 1-2 and 2-1 alignments, but only with colours.<br>The hotter the colour, the higher the score</html>");
		matchInfoList.setToolTipText("<html>Information about how well the pending elements match,<br>with details about anchor word matches, Dice, etc.<br>Note: The information is based solely on the pending elements.<br>There is no consideration of the path of alignments ahead.<br>Note: The elements under consideration may belong to more than one alignment<br>(they have more than one colour), but this box doesn't know anything about that</html>");

        for (int t=0; t<Alignment.NUM_FILES; t++) {

			openFileButton[t].setToolTipText("Open text " + (t+1));

			alignedListBox[t].setToolTipText("Contains the aligned elements of text " + (t+1));

			toAlignListBox[t].setToolTipText("<html>Contains element(s) pending for alignment, from text " + (t+1) + ".<br>Click elements to change their belonging to alignments<html>");
			moreButton[t].setToolTipText("Move one unaligned element up in text " + (t+1));
			lessButton[t].setToolTipText("Drop one pending element in text " + (t+1));
			unalignedListBox[t].setToolTipText("Contains the not yet aligned elements of text " + (t+1));
		}

		////////////
		// layout //
		////////////

        layout = new GridBagLayout();
        setLayout(layout);
        GridBagConstraints c = new GridBagConstraints();
        c.insets = new Insets(3,3,3,3);
		c.anchor = GridBagConstraints.NORTH;
        AwtUtil util = new AwtUtil(this, layout, c);

        //// colours
        // set background colour


        //// Marlén's colours
        //Color bgColor = new Color(0xF5DEB3);   // #F5DEB3

        this.setBackground(bgColor);
        menuBar.setBackground(buttonColor);

        JScrollPane s;

		// first row - file buttons and labels

		c.gridy = FILE_ROW;
		c.weighty = FILE_ROW_WEIGHT;

        for (int t=0; t<Alignment.NUM_FILES; t++) {

			c.gridx = TEXT_COLS[t];
			c.gridwidth = 1;
			c.weightx = TEXT_COL_WEIGHT;
			c.fill = GridBagConstraints.HORIZONTAL;

			// color
			openFileButton[t].setBackground(buttonColor);
			openFileButton[t].setForeground(buttonTextColor);

			Box b1 = new Box(BoxLayout.X_AXIS);
			if (t<Alignment.NUM_FILES-1) {
				b1.add(openFileButton[t]);
				b1.add(Box.createHorizontalGlue());
				b1.add(filenameLabel[t]);
				b1.add(Box.createHorizontalGlue());
			} else {
				b1.add(Box.createHorizontalGlue());
				b1.add(filenameLabel[t]);
				b1.add(Box.createHorizontalGlue());
				b1.add(openFileButton[t]);
			}

			b1.setOpaque(false);

			util.addInGridBag(b1);
		}

		c.gridx = DO_COL;
		c.gridwidth = 1;
		c.weightx = DO_COL_WEIGHT;
		c.fill = GridBagConstraints.NONE;

		// ¤¤¤ options

		{
			// color
			saveAllFileButton.setBackground(buttonColor);
			saveAllFileButton.setForeground(buttonTextColor);
			purgeButton.setBackground(buttonColor);
			purgeButton.setForeground(buttonTextColor);

			savePurgePanel.setBackground(this.getBackground());
			savePurgePanel.add(saveAllFileButton);
			savePurgePanel.add(purgeButton);
			savePurgePanel.setAlignmentX(0.0f);   // ###

			savePurgePanel.setOpaque(false);

			Box b = new Box(BoxLayout.X_AXIS);
			b.add(savePurgePanel);

			b.setOpaque(false);

			util.addInGridBag(b);
		}

		// second row - aligned elements

		c.gridy = ALIGNED_ROW;
		c.weighty = ALIGNED_ROW_WEIGHT;

        for (int t=0; t<Alignment.NUM_FILES; t++) {

			c.gridx = TEXT_COLS[t];
			c.gridwidth = 1;
			c.weightx = TEXT_COL_WEIGHT;
			c.fill = GridBagConstraints.BOTH;

			alignedScrollPane[t] = new JScrollPane(alignedListBox[t]);
			alignedScrollPane[t].setHorizontalScrollBarPolicy(ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER);
			alignedScrollPane[t].setVerticalScrollBarPolicy(ScrollPaneConstants.VERTICAL_SCROLLBAR_ALWAYS);   // 2006-09-15

			util.addInGridBag(alignedScrollPane[t]);

		}

		c.gridx = DO_COL;
		c.gridwidth = 1;
		c.weightx = DO_COL_WEIGHT;
		c.fill = GridBagConstraints.BOTH;

		// color
		anchorFileButton.setBackground(buttonColor);
		anchorFileButton.setForeground(buttonTextColor);
		settingsButton.setBackground(buttonColor);
		settingsButton.setForeground(buttonTextColor);
		settingsPanel.setBackground(this.getBackground());
		logPanel.setBackground(this.getBackground());
		startLoggingButton.setBackground(buttonColor);
		startLoggingButton.setForeground(buttonTextColor);
		startLoggingButton.setVisible(!model.logging);
		stopLoggingButton.setBackground(buttonColor);
		stopLoggingButton.setForeground(buttonTextColor);
		stopLoggingButton.setVisible(model.logging);
		breakButton.setBackground(buttonColor);   // 2006-08-15
		breakButton.setForeground(buttonTextColor);   // 2006-08-15
		skipButton.setBackground(buttonColor);
		skipButton.setForeground(buttonTextColor);
		skipPanel.setForeground(buttonTextColor);
		skipPanel.setBackground(this.getBackground());
		breakPanel.setForeground(buttonTextColor);   // 2006-08-15
		breakPanel.setBackground(this.getBackground());   // 2006-08-15
		runPanel.setBackground(this.getBackground());
		runLimitLabel1.setBackground(this.getBackground());
		runLimitLabel1.setFont(plainFont);
		runLimitLabel2.setBackground(this.getBackground());
		runLimitLabel2.setFont(plainFont);
		modeRadioButtonPanel.setBackground(this.getBackground());

		unalignButton.setBackground(buttonColor);
		unalignButton.setForeground(buttonTextColor);
		alignButton.setBackground(buttonColor);
		alignButton.setForeground(buttonTextColor);

		Box anchorFileBox = new Box(BoxLayout.Y_AXIS);
		anchorFileBox.add(anchorFileButton);
		anchorFileBox.add(anchorFilenameLabel);

		Box settingsFileBox = new Box(BoxLayout.Y_AXIS);   // 2006-09-21
		settingsFileBox.add(settingsButton);   // 2006-09-21
		settingsFileBox.add(settingsFilenameLabel);   // 2006-09-21

		settingsPanel.add(anchorFileBox);
		settingsPanel.add(settingsFileBox);   // 2006-09-21
		settingsPanel.setAlignmentX(0.0f);   // ###
		settingsPanel.setAlignmentY(0.0f);   // ### hjalp ikke. hadde håpet at knappen ble stående i flukt med anker-knappen, også etter at ankerfil valgt
		settingsPanel.setOpaque(false);

		Box logButtonsBox = new Box(BoxLayout.Y_AXIS);
		logButtonsBox.add(startLoggingButton);
		logButtonsBox.add(stopLoggingButton);
		Box logBox = new Box(BoxLayout.Y_AXIS);
		logBox.add(logButtonsBox);
		logBox.add(logFilenameLabel);
		logPanel.add(logBox);
		logPanel.setAlignmentX(0.0f);   // ###
		logPanel.setOpaque(false);

		runPanel.add(runLimitLabel1);
		runPanel.add(runLimitTextField);
		runPanel.add(runLimitLabel2);

		modeRadioButtonPanel.setAlignmentX(0.0f);   // ###
		modeRadioButtonPanel.setOpaque(false);
		runPanel.setAlignmentX(0.0f);   // ###
		runPanel.setOpaque(false);

		skipPanel.add(skipButton);
		skipPanel.setAlignmentX(0.0f);   // ###

		skipPanel.setOpaque(false);

		breakPanel.add(breakButton);   // 2006-08-15
		breakPanel.setAlignmentX(0.0f);   // ###    // 2006-08-15

		breakPanel.setOpaque(false);   // 2006-08-15

		unalignButton.setMaximumSize(new Dimension(300, 0));
		alignButton.setMaximumSize(new Dimension(300, 0));

		Box b2 = new Box(BoxLayout.Y_AXIS);
		b2.add(Box.createVerticalGlue());
		b2.add(settingsPanel);
		b2.add(logPanel);
		b2.add(skipPanel);
		b2.add(Box.createVerticalGlue());
		b2.add(modeRadioButtonPanel);
		b2.add(runPanel);
		b2.add(Box.createVerticalGlue());
		b2.add(Box.createVerticalStrut(6));
		b2.add(unalignButton);
		b2.add(Box.createVerticalStrut(6));
		b2.add(alignButton);

		b2.setOpaque(false);

		util.addInGridBag(b2);

		// for resizing purposes
		row2 = new Component[Alignment.NUM_FILES + 1];
		row2[0] = alignedListBox[0];
		row2[1] = b2;
		row2[2] = alignedListBox[1];
		row2weighty = c.weighty;

		// third row - elements under consideration for alignment

		c.gridy = WORK_ROW;
		c.weighty = WORK_ROW_WEIGHT;

        for (int t=0; t<Alignment.NUM_FILES; t++) {

			c.gridx = TEXT_COLS[t];
			c.gridwidth = 1;
			c.weightx = TEXT_COL_WEIGHT;
			c.fill = GridBagConstraints.BOTH;

			toAlignScrollPane[t] = new JScrollPane(toAlignListBox[t]);
			toAlignScrollPane[t].setHorizontalScrollBarPolicy(ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER);
			toAlignScrollPane[t].setVerticalScrollBarPolicy(ScrollPaneConstants.VERTICAL_SCROLLBAR_ALWAYS);   // 2006-09-15
			util.addInGridBag(toAlignScrollPane[t]);

		}

		c.gridx = DO_COL;
		c.gridwidth = 1;
		c.weightx = DO_COL_WEIGHT;
		c.fill = GridBagConstraints.BOTH;

		Box b3 = new Box(BoxLayout.X_AXIS);
		compareInfoScrollPane.setMaximumSize(new Dimension(300, Integer.MAX_VALUE));
		b3.add(compareInfoScrollPane);

		b3.setOpaque(false);

		util.addInGridBag(b3);

		// for resizing purposes
		row3 = new Component[Alignment.NUM_FILES + 1];
		row3[0] = toAlignListBox[0];
		row3[1] = toAlignListBox[1];

		// fourth row - less/more buttons

		c.gridy = CHANGE_ROW;
		c.weighty = CHANGE_ROW_WEIGHT;

        for (int t=0; t<Alignment.NUM_FILES; t++) {

			c.gridx = TEXT_COLS[t];
			c.gridwidth = 1;
			c.weightx = TEXT_COL_WEIGHT;
			c.fill = GridBagConstraints.HORIZONTAL;

			// color
			lessButton[t].setBackground(buttonColor);
			lessButton[t].setForeground(buttonTextColor);
			moreButton[t].setBackground(buttonColor);
			moreButton[t].setForeground(buttonTextColor);

			Box b = new Box(BoxLayout.X_AXIS);
			//b.add(moreLessArrow[t]);
			//b.add(Box.createHorizontalGlue());
			lessButton[t].setMaximumSize(new Dimension(Integer.MAX_VALUE, Integer.MAX_VALUE));
			moreButton[t].setMaximumSize(new Dimension(Integer.MAX_VALUE, Integer.MAX_VALUE));
			if (t == 0) {
				b.add(lessButton[t]);
			} else {
				b.add(moreButton[t]);
			}
			b.add(Box.createRigidArea(new Dimension(6, 0)));   // 6 passer bedre siden insets er 3
			if (t == 0) {
				b.add(moreButton[t]);
			} else {
				b.add(lessButton[t]);
			}

			b.setOpaque(false);

			util.addInGridBag(b);

		}

		c.gridx = DO_COL;
		c.gridwidth = 1;
		c.weightx = DO_COL_WEIGHT;
		c.fill = GridBagConstraints.HORIZONTAL;

		// color
		suggestButton.setBackground(buttonColor);
		suggestButton.setForeground(buttonTextColor);

		Box b5 = new Box(BoxLayout.Y_AXIS);
		b5.add(suggestButton);
		suggestButton.setMaximumSize(new Dimension(300, Integer.MAX_VALUE));

		b5.setOpaque(false);

		util.addInGridBag(b5);

		// fifth row - unaligned elements

		c.gridy = UNALIGNED_ROW;
		c.weighty = UNALIGNED_ROW_WEIGHT;

        for (int t=0; t<Alignment.NUM_FILES; t++) {

			c.gridx = TEXT_COLS[t];
			c.gridwidth = 1;
			c.weightx = TEXT_COL_WEIGHT;
			c.fill = GridBagConstraints.BOTH;

			unalignedScrollPane[t] = new JScrollPane(unalignedListBox[t]);
			unalignedScrollPane[t].setHorizontalScrollBarPolicy(ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER);
			unalignedScrollPane[t].setVerticalScrollBarPolicy(ScrollPaneConstants.VERTICAL_SCROLLBAR_ALWAYS);   // 2006-09-15

			util.addInGridBag(unalignedScrollPane[t]);

		}

		c.gridx = DO_COL;
		c.gridwidth = 1;
		c.weightx = DO_COL_WEIGHT;
		c.fill = GridBagConstraints.BOTH;

		compareInfoScrollPane.setMinimumSize(new Dimension(MIN_DO_WIDTH, MIN_WORK_HEIGHT));
		matchInfoScrollPane.setMaximumSize(new Dimension(300, Integer.MAX_VALUE));
		util.addInGridBag(matchInfoScrollPane);

		// for resizing purposes
		row5 = new Component[Alignment.NUM_FILES + 1];
		row5[0] = unalignedListBox[0];
		//row5[1] = b5;
		row5[1] = matchInfoScrollPane;
		row5[2] = unalignedListBox[1];
		row5weighty = c.weighty;

		// sixth row - status line

		c.gridy = STATUS_ROW;
		c.weighty = STATUS_ROW_WEIGHT;

		c.gridx = 0;
		c.gridwidth = GridBagConstraints.REMAINDER;
		c.weightx = 0;
		c.fill = GridBagConstraints.BOTH;

		util.addInGridBag(statusLine);

		model.currentOpenDirectory = null;
		model.currentSaveDirectory = null;

    } //end constructor

} //end class AlignGui


