/*
 * AnchorDialog.java
 *
 * ...
 * ...
 * ...
 */

package aksis.alignment;

// ¤¤¤ ikke sjekket nøyaktig hva vi trenger
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import java.util.*;
import java.lang.String;
import java.io.*;
import java.nio.charset.*;
//import java.awt.Toolkit;   // beep
//import aksis.awt2.AwtUtil;   // Oystein flyttet denne inn sammen med alt det andre. den var så ensom der den satt helt for seg selv

class AnchorDialog extends JDialog {

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	boolean approved;   // ¤¤¤ er dette måten å returnere data på? kan ikke være private.

	private JButton openFileButton;   // open file containing anchor word list
	private JButton saveFileButton;   // save file
	private JTextArea content;   // component for display and editing of anchor word list
	private JScrollPane contentScrollPane;
	private JButton useButton;   // approve use of the current anchor word list, and close
	private JButton cancelButton;   // close, and don't use current anchor word list

	// 2005-05-18. member for remembering the current directory.
	// ¤¤¤ can't seem to have a current _file_
	//// current file. there doesn't need to be one.
	//// if a file has been opened and read into the 'content' text area there is a current file.
	//// if no file has been opened, there is no current file.
	//// (the user may create an anchor word list from scratch
	//// by entering data in the text area and save the result to a file.)
	//// if the user does a save, the current file is the default target.
	//// if the user does another open, the current file is the default source.
	//private File currentDirectory; ¤¤¤ 2005-08-19 rather use the main window's current open-directory

    protected OpenAction openAction;
    protected SaveAction saveAction;

    AlignmentModel model;    // package access  // 2006-09-21 ###hvorfor også model som parameter i loadFile()?
    AlignGui gui;

    //public AnchorDialog(JFrame parent, AlignmentModel model) {
    //public AnchorDialog(JFrame parent, AlignmentModel model, int entryNumber) {
    public AnchorDialog(JFrame parent, AlignGui gui, int entryNumber) {

		//

		super(parent, "Anchor word list", true);

		//

        this.gui = gui;
        //this.model = model;
        this.model = gui.model;

		//

		OpenAction openAction = new
			OpenAction(
				"Open anchor word file",
				createImageIcon("images/Read.gif", "read from disc"),
				"Open anchor word file",
				new Integer(0)
			);

		SaveAction saveAction = new
			SaveAction(
				"Save anchor word file",
				createImageIcon("images/Write.gif", "write to disc"),
				"Save anchor word file",
				new Integer(0)
			);

		UseAction useAction = new
			UseAction(
				"Use this anchor word list",
				//createImageIcon("images/Use.gif", "a face"),   // §§§ finnes ikke
				createImageIcon("images/Select.gif", "'ticked' symbol"),
				"Use this anchor word list",
				new Integer(0)
			);

		CancelAction cancelAction = new
			CancelAction(
				"Cancel",
				//createImageIcon("images/Cancel.gif", "a face"),   // §§§ finnes ikke
				createImageIcon("images/Cancel.gif", "'X' symbol"),
				"Cancel",
				new Integer(0)
			);

		//

		content = new JTextArea();
		contentScrollPane = new JScrollPane(content);

		openFileButton = new JButton(openAction);
		openFileButton.setName("O");   // ¤¤¤ husker ikke om dette kan brukes til noe

		saveFileButton = new JButton(saveAction);
		saveFileButton.setName("S");   // ¤¤¤ husker ikke om dette kan brukes til noe

		useButton = new JButton(useAction);
		useButton.setName("U");   // ¤¤¤ husker ikke om dette kan brukes til noe

		cancelButton = new JButton(cancelAction);
		cancelButton.setName("C");   // ¤¤¤ husker ikke om dette kan brukes til noe

		//

		//openFileButton = new JButton("Open anchor word file");
		//saveFileButton = new JButton("Save anchor word file");
		//useButton = new JButton("Use this anchor word list");   // men må være lagret først (?)
		//cancelButton = new JButton("Cancel");

        Container cp = new Container();
        cp = getContentPane();
        GridBagLayout layout = new GridBagLayout();
        cp.setLayout(layout);
        GridBagConstraints c = new GridBagConstraints();
        c.insets = new Insets(3,3,3,3);
        AwtUtil util = new AwtUtil(cp, layout, c);

        // ¤¤¤ vet ikke hvorfor innholdet ikke utvider seg i bredden ved resizing

        // open/file buttons

		c.gridy = 0;
		c.weighty = 0;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;

		Box b1 = new Box(BoxLayout.X_AXIS);
		b1.add(openFileButton);
		b1.add(Box.createHorizontalGlue());
		b1.add(saveFileButton);

		util.addInGridBag(b1);

        // content text area

		c.gridy = 1;
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.BOTH;

		util.addInGridBag(contentScrollPane);

		// display current anchor word list
		this.model.anchorWordList.display(content);

        // ok/cancel buttons

		c.gridy = 2;
		c.weighty = 0;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;

		Box b2 = new Box(BoxLayout.X_AXIS);
		b2.add(useButton);
		b2.add(Box.createHorizontalGlue());
		b2.add(cancelButton);

		util.addInGridBag(b2);

		//

		//openFileButton.addActionListener(new ActionListener() {
		//	public void actionPerformed(ActionEvent e) {
		//		// ...
		//		Toolkit.getDefaultToolkit().beep();
		//	}
		//});
		//
		//saveFileButton.addActionListener(new ActionListener() {
		//	public void actionPerformed(ActionEvent e) {
		//		// ...
		//		Toolkit.getDefaultToolkit().beep();
		//	}
		//});
		//
		//useButton.addActionListener(new ActionListener() {
		//	public void actionPerformed(ActionEvent e) {
		//		// ...
		//		Toolkit.getDefaultToolkit().beep();
		//		approved = true;
		//		hide();
		//	}
		//});
		//
		//cancelButton.addActionListener(new ActionListener() {
		//	public void actionPerformed(ActionEvent e) {
		//		// ...
		//		Toolkit.getDefaultToolkit().beep();
		//		approved = false;
		//		hide();
		//	}
		//});

		// shortcuts

		openFileButton.setMnemonic(KeyEvent.VK_O);
		saveFileButton.setMnemonic(KeyEvent.VK_S);
		useButton.setMnemonic(KeyEvent.VK_U);   // Use
		cancelButton.setMnemonic(KeyEvent.VK_C);

		// tool tip

		openFileButton.setToolTipText("Open file containing anchor word list, and display the contents");
		saveFileButton.setToolTipText("Save the currently anchor word list to file");
		content.setToolTipText("Area where an anchor word list can be displayed and created/edited");
		useButton.setToolTipText("Use the currently showing anchor word list");   // §§§  (must be saved to file first)????????
		cancelButton.setToolTipText("Don't use the currently showing anchor word list");

		// go directly to one particular line?

		// ### cludgy
		if (entryNumber >= 0) {

			// yes. go directly to one particular line

			// hvordan får jeg denne til å rulle til rett linje? contentScrollPane.
			//select(int selectionStart, int selectionEnd);
			String cont = content.getText();
			int pos = 0;
			for (int i=0; i<=entryNumber; i++) {
				int newPos = cont.indexOf("\n", pos);
				if (newPos == -1) {
					pos = cont.length();
					break;
				} else {
					pos = newPos + 1;
				}
				//System.out.println("i = " + i + ". pos = " + pos);
			}
			pos--;   // go back, before \n. ### what if no \n at very end?
			content.setCaretPosition(pos);
			//content.requestFocus();
			content.requestFocusInWindow();   // ### funker ikke. må visst gjøres på et helt bestemt tidspunkt

		}

		//

		Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();   // §§§ ikke brukt

		setSize(400, 400);

		//currentDirectory = null;

	}

	// 2005-05-18. i AlignGui har jeg slike actions.
	// de er kanskje nyttigere der samme action skal startes på mange måter:
	// knapp, meny, hurtigtast.
	// her i denne dialogen er det ikke meny.
	// men actions er sikkert en veldig skikkelig måte å gjøre det på.
	// så jeg gjør det her også

	// §§§ skulle denne vært gjenbrukt? er i både AlignGui og Settings og her
	public abstract class MyAbstractAction extends AbstractAction {
		public MyAbstractAction(String text, ImageIcon icon, String desc, Integer mnemonic) {
			super(text, icon);
			putValue(SHORT_DESCRIPTION, desc);
			putValue(MNEMONIC_KEY, mnemonic);
		}
	}

	public class OpenAction extends MyAbstractAction {
		public OpenAction(String text, ImageIcon icon, String desc, Integer mnemonic) {
			super(text, icon, desc, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {

			//String command = e.getActionCommand();   // ¤¤¤ kan også fjernes fra AlignGui
			//System.out.println("command er " + command);

			// check if there is content in the 'content' text area already

			/* ¤¤¤ getText
			public String getText()Returns the text contained in this TextComponent. If the underlying document is null, will give a NullPointerException. Note that text is not a bound property, so no PropertyChangeEvent is fired when it changes. To listen for changes to the text, use DocumentListener.
			Returns:
			the text
			Throws:
			NullPointerException - if the document is null
			See Also:
			setText(java.lang.String) */

			boolean ok;
			//System.out.println("content=" + content.getText() + "!");
			//if (content.getText() == "") {   // ¤¤¤ null var feil? "" var feil?
			if (content.getText().length() == 0) {   // ¤¤¤ men dette funker
				// no content
				//System.out.println("no content");
				ok = true;
			} else {
				// there is content
				//System.out.println("there is content");
				// ¤¤¤eller skal det være WARNING_MESSAGE?
				// ¤¤¤ 0 = YES, 1 = NO?
				ok = (
					JOptionPane.showConfirmDialog(
						null,
						"¤¤¤Overwrite current content?",
						//"¤¤¤Title",
						"Error",   // 2006-09-21
						JOptionPane.YES_NO_OPTION,
						JOptionPane.QUESTION_MESSAGE) == 0
				);
			}

			if (ok) {

				JFileChooser chooser = new JFileChooser();
				chooser.setApproveButtonText("Open anchor word file");
				//if (currentDirectory != null) {
				//	chooser.setCurrentDirectory(currentDirectory);
				//} else {
				//	chooser.setCurrentDirectory(null);
				//}
				if (model.currentOpenDirectory != null) {
					chooser.setCurrentDirectory(model.currentOpenDirectory);
				} else {
					chooser.setCurrentDirectory(null);
				}

				int returnVal = chooser.showOpenDialog(AnchorDialog.this);   // arg får open-dialog til å ligge sentrert over anchor-dialog. hvis null havner open-dialog i senter av skjerm
				if(returnVal == JFileChooser.APPROVE_OPTION) {
					////System.out.println("chooser.getSelectedFile() = " + chooser.getSelectedFile());
					//if (loadFile(chooser.getSelectedFile())) {
					if (loadFile(model, chooser.getSelectedFile())) {
						//...;   ¤¤¤
					} else {
						//...;   ¤¤¤
					}
					model.currentOpenDirectory = chooser.getCurrentDirectory();
				}

			}

		}
	}

	public class SaveAction extends MyAbstractAction {
		public SaveAction(String text, ImageIcon icon, String desc, Integer mnemonic) {
			super(text, icon, desc, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {

			String command = e.getActionCommand();
			//System.out.println("command er " + command);

			JFileChooser chooser = new JFileChooser();
			chooser.setApproveButtonText("Save anchor word file");
			//if (currentDirectory != null) {
			//	chooser.setCurrentDirectory(currentDirectory);
			//} else {
			//	chooser.setCurrentDirectory(null);
			//}
			if (model.currentSaveDirectory != null) {
				chooser.setCurrentDirectory(model.currentSaveDirectory);
			} else if (model.currentOpenDirectory != null) {
				chooser.setCurrentDirectory(model.currentOpenDirectory);
			} else {
				chooser.setCurrentDirectory(null);
			}

			int returnVal = chooser.showSaveDialog(AnchorDialog.this);   // arg får open-dialog til å ligge sentrert over anchor-dialog. hvis null havner open-dialog i senter av skjerm
			if(returnVal == JFileChooser.APPROVE_OPTION) {

				////System.out.println("chooser.getSelectedFile() = " + chooser.getSelectedFile());

				File f = chooser.getSelectedFile();

				boolean doSave;
				if(f.exists()) {
					//System.out.println("f.exists()");
					//Object[] options = { "Yessir", "Nope" };   // button texts
					Object[] options = { "Yes", "No" };   // button texts
					int n = JOptionPane.showOptionDialog(
						null,
						f.getAbsolutePath() + "\n" + "already exist.\n\n" + "Overwrite file?",
						"File exists",
						JOptionPane.YES_NO_OPTION,
						JOptionPane.QUESTION_MESSAGE,
						null,
						options,
						options[0]   // the choice that is initially selected
					);
					if(n == 0) {
						// YES
						//System.out.println("n == 1");
						doSave = true;
					} else {
						// NO
						//System.out.println("n != 1");
						doSave = false;
					}
				} else {
					doSave = true;
					//System.out.println("!f.exists()");
				}

				if (doSave) {   // 2006-09-20b. ########ikke testet
					if (saveFile(f)) {
						//...;   ¤¤¤
					} else {
						//...;   ¤¤¤
					}
				}   // 2006-09-20b
			}
			//#####// §§§§§§§§§§§ verken her eller i AlignGui er det sjekk på om filen finnes fra før

		}
	}

	public class UseAction extends MyAbstractAction {
		public UseAction(String text, ImageIcon icon, String desc, Integer mnemonic) {
			super(text, icon, desc, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {

			String command = e.getActionCommand();
			//System.out.println("command er " + command);
			//System.out.println("\n\nuse\n\n");

			//
			ArrayList list = new ArrayList(Arrays.asList(content.getText().split("\\n")));  // ¤¤¤ load() tar trim(). hvem sin jobb er det?
			//System.out.println("list.size()=" + list.size());
			AnchorDialog.this.model.anchorWordList.load(list);
			//System.out.println("AnchorDialog.this.model.anchorWordList.entries.size() = " + AnchorDialog.this.model.anchorWordList.entries.size());

			AnchorDialog.this.approved = true;

			//... lukk. hvordan??? hide() ???????????????????
			AnchorDialog.this.dispose();

		}
	}

	public class CancelAction extends MyAbstractAction {
		public CancelAction(String text, ImageIcon icon, String desc, Integer mnemonic) {
			super(text, icon, desc, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {

			String command = e.getActionCommand();
			//System.out.println("command er " + command);

			AnchorDialog.this.approved = false;

			//... lukk. hvordan??? hide() ???????????????????
			AnchorDialog.this.dispose();   // ser ut til å funke

		}
	}

    //private boolean loadFile(File f) {
    private boolean loadFile(AlignmentModel model, File f) {

        try {

			//FileInputStream fileInputStream = new FileInputStream(f);
			//¤¤¤2006-02-21. lese utf-8. ankerordsfil må nå være utf-8
			InputStream fIn = new FileInputStream(f);
			InputStream bIn = new BufferedInputStream(fIn);
			Charset cs = Charset.forName("UTF-8");
			InputStreamReader in = new InputStreamReader(bIn, cs);

			int iChar;
			while ((iChar = in.read()) != -1) {
				content.append("" + (char)iChar);
			}
			in.close();

			// ... file name ...
			model.setAnchorFilename(f.getName());
			// also show in gui
			gui.setAnchorFilenameLabel(f.getName());

            return true;

        } catch (Exception e) {
		//} catch (IOException e) { kanskje heller bruke denne ############

			// ¤¤¤ PLAIN_MESSAGE, INFORMATION_MESSAGE, WARNING_MESSAGE, ERROR_MESSAGE?
			//¤¤¤ advarselsdialog her eller i kallende kode?
			/* // 2006-09-21
			JOptionPane.showMessageDialog(
				null,
				"Can't load file " + f.getName(),
				//"¤¤¤Title",
				"Error",   // 2006-09-21
				JOptionPane.ERROR_MESSAGE
			);
            //System.err.println("Exception when loading " + f.getName() + ": ");
            //System.err.println(e.toString());
            ErrorMessage.error("Exception when loading " + f.getName() + ":\n" + e.toString());   // 2006-08-10
            //e.printStackTrace();
            */
            ErrorMessage.error("Can't load file " + f.getName() + "\nException:\n" + e.toString());   // 2006-09-21

            return false;

        }

    }

    private boolean saveFile(File f) {

        try {

			//// §§§§§§§ FileOutputStream is meant for writing streams of raw bytes such as image data. For writing streams of characters, consider using FileWriter.
			//FileWriter fileWriter = new FileWriter(f);
			//¤¤¤2006-02-21. skrive utf-8. ankerordsfil må nå være utf-8
			OutputStream fOut = new FileOutputStream(f);
			OutputStream bOut = new BufferedOutputStream(fOut);
			Charset cs = Charset.forName("UTF-8");
			OutputStreamWriter out = new OutputStreamWriter(bOut, cs);

			out.write(content.getText(), 0, content.getText().length());
			out.close();

			// ... file name ...
			model.setAnchorFilename(f.getName());
			// also show in gui
			gui.setAnchorFilenameLabel(f.getName());

            return true;

        } catch (Exception e) {
		//} catch (IOException e) { kanskje heller bruke denne ############

			// ¤¤¤ PLAIN_MESSAGE, INFORMATION_MESSAGE, WARNING_MESSAGE, ERROR_MESSAGE?
			//¤¤¤ advarselsdialog her eller i kallende kode?
			/* // 2006-09-21
			JOptionPane.showMessageDialog(
				null,
				"Can't save file " + f.getName(),
				//"¤¤¤Title",
				"Error",   // 2006-09-21
				JOptionPane.ERROR_MESSAGE
			);
            //System.err.println("Exception when saving " + f.getName() + ": ");
            //System.err.println(e.toString());
            ErrorMessage.error("Exception when saving " + f.getName() + ":\n" + e.toString());   // 2006-08-10
            //e.printStackTrace();
            */
            ErrorMessage.error("Can't save file " + f.getName() + "\nException:\n" + e.toString());   // 2006-09-21

            return false;

        }

    }

	// hvor skal denne? §§§nå er den både i AlignGui og Settings og her
	/** Returns an ImageIcon, or null if the path was invalid. */
	protected static ImageIcon createImageIcon(String path, String description) {
		java.net.URL imgURL = AnchorDialog.class.getResource(path);
		if (imgURL != null) {
			return new ImageIcon(imgURL, description);
		} else {
			//System.err.println("Couldn't find file: " + path);
			return null;
		}
	}

}
