/*
 * Alignment.java
 *
 * ...
 * ...
 * ...
 */

package aksis.alignment;

import javax.swing.*;
import java.awt.*;
import java.io.*;
import java.nio.charset.*;

/**
 * Program startup class for alignment project.
 * @author Johan Utne Poppe
 */


public class Alignment {

	public static final String VERSION = "2007-01-04";

	// ### alt eller noe av dette hører hjemme i model

	// the number of texts to align

	public static final int NUM_FILES = 2;

	// with the following settings we get 1-1, 0-1, 1-0, 1-2, 2-1 and 2-2 comparisons,
	// but e.g not 0-2, 2-0, 1-3, 3-3.
	// (neither do we get 0-0 comparisons because they make no sense.)
	// when trying to align elements the program
	// must select at least 0 elements from each text
	public static final int MIN_NUM_TRY = 0;
	// when trying to align elements the program
	// must select at most 2 elements from each text
	public static final int MAX_NUM_TRY = 2;
	// when trying to align elements the number of elements
	// selected from each text cannot differ by more than 1
	public static final int MAX_DIFF_TRY = 1;
	// when trying to align elements the total number of elements
	// selected from the texts cannot exceed 3
	public static final int MAX_TOTAL_TRY = 3;

	public static final String DEFAULT__SETTINGS_FILENAME = ".\\tca2.cfg";

	public static final String DEFAULT__RELEVANT_ELEMENT_NAMES = "s head";
	public static final String DEFAULT__RELEVANT_ANCESTOR_ELEMENT_NAMES = "p div";

	public static final String DEFAULT__SPECIAL_CHARACTERS = ".,;:?!&^(){}[]'" + '"';   // characters that will be stripped off words (unless they are in the middle of words)
	public static final String DEFAULT__SCORING_CHARACTERS = "§?!%";   // characters that add to the score if they occur in both tetxt

	public static final float DEFAULT__LENGTH_RATIO = 1.1f;
	public static final float MIN__LENGTH_RATIO = 0.5f;   // least allowable value of the above
	public static final float MAX__LENGTH_RATIO = 2.f;   // greatest allowable value of the above
	public static final float STEP__LENGTH_RATIO = 0.01f;   // step in the spinner component of the above

    public static final int DEFAULT__DICE_MIN_WORD_LENGTH = 5;   // default. user settable. words with length below this value will not be compared
    public static final int MIN__DICE_MIN_WORD_LENGTH = 1;   // least possible value of the above

	public static final float DEFAULT__DICE_MIN_COUNTING_SCORE = 0.7f;   // word pairs with raw dice score below this value will not get a score
	public static final float MIN__DICE_MIN_COUNTING_SCORE = 0.5f;   // least allowable value of the above
	public static final float MAX__DICE_MIN_COUNTING_SCORE = 0.9f;   // greatest allowable value of the above
	public static final float STEP__DICE_MIN_COUNTING_SCORE = 0.01f;   // step in the spinner component of the above
    public static final int MIN__LARGE_CLUSTER_SCORE_PERCENTAGE = 0;
    public static final int MAX__LARGE_CLUSTER_SCORE_PERCENTAGE = 100;
    public static final int DEFAULT__LARGE_CLUSTER_SCORE_PERCENTAGE = 25;
    public static final int STEP__LARGE_CLUSTER_SCORE_PERCENTAGE = 5;

    public static final int DEFAULT__MAX_PATH_LENGTH = 10;
    public static final int MAX__MAX_PATH_LENGTH = 20;

	public static final float MIN__ANCHORWORD_MATCH_WEIGHT       = 0.5f;
    public static final float MAX__ANCHORWORD_MATCH_WEIGHT       = 3.0f;

    public static final float MIN__ANCHORPHRASE_MATCH_WEIGHT     = 0.5f;
    public static final float MAX__ANCHORPHRASE_MATCH_WEIGHT     = 3.0f;

    public static final float MIN__PROPERNAME_MATCH_WEIGHT       = 0.5f;
    public static final float MAX__PROPERNAME_MATCH_WEIGHT       = 3.0f;

    public static final float MIN__DICE_MATCH_WEIGHT             = 0.5f;
    public static final float MAX__DICE_MATCH_WEIGHT             = 3.0f;

    public static final float MIN__DICEPHRASE_MATCH_WEIGHT       = 0.5f;
    public static final float MAX__DICEPHRASE_MATCH_WEIGHT       = 3.0f;

    public static final float MIN__NUMBER_MATCH_WEIGHT           = 0.5f;
    public static final float MAX__NUMBER_MATCH_WEIGHT           = 3.0f;

    public static final float MIN__SCORINGCHARACTER_MATCH_WEIGHT = 0.5f;
    public static final float MAX__SCORINGCHARACTER_MATCH_WEIGHT = 3.0f;
    
    public static final float STEP__MATCH_WEIGHT = 0.1f;
    public static final float DEFAULT__ANCHORWORD_MATCH_WEIGHT       = 1.0f;
    public static final float DEFAULT__ANCHORPHRASE_MATCH_WEIGHT     = 1.6f;
    public static final float DEFAULT__PROPERNAME_MATCH_WEIGHT       = 3.0f;
    public static final float DEFAULT__DICE_MATCH_WEIGHT             = 1.3f;
    public static final float DEFAULT__DICEPHRASE_MATCH_WEIGHT       = 3.0f;
    public static final float DEFAULT__NUMBER_MATCH_WEIGHT           = 3.0f;
    public static final float DEFAULT__SCORINGCHARACTER_MATCH_WEIGHT = 0.5f;

	public static final int MODE_ONE = 1;
	public static final int MODE_SKIP11 = 2;
	public static final int MODE_AUTO = 3;


    // In many circumstances, you need a chance to do some clean-up when the user shuts down your application...
    // <http://www.onjava.com/pub/a/onjava/2003/03/26/shutdownhook.html#listing1>
	public void start(AlignmentModel model) {
		ShutdownHook shutdownHook = new ShutdownHook(model);
		Runtime.getRuntime().addShutdownHook(shutdownHook);

	}

    public static void main(String[] args) throws Exception {

		AlignmentModel model = new AlignmentModel();

		// <http://www.onjava.com/pub/a/onjava/2003/03/26/shutdownhook.html#listing1>
		// model must exist before start() is run, because the latter needs it
		Alignment alignment = new Alignment();
		alignment.start(model);

		AlignGui gui;

		// command line parameters
        // <http://www.javaworld.com/javaworld/jw-08-2004/jw-0816-command-p4.html>

		Options opt = new Options(args);

		opt.getSet().addOption("cfg", Options.Separator.EQUALS, Options.Multiplicity.ZERO_OR_ONE);   // name of file with settings
		opt.getSet().addOption("cli", Options.Multiplicity.ZERO_OR_ONE);
		opt.getSet().addOption("cli-plain", Options.Multiplicity.ZERO_OR_ONE);
		opt.getSet().addOption("anchor", Options.Separator.EQUALS, Options.Multiplicity.ZERO_OR_ONE); // anchor file name
		opt.getSet().addOption("in1", Options.Separator.EQUALS, Options.Multiplicity.ZERO_OR_ONE); // first input file name
		opt.getSet().addOption("in2", Options.Separator.EQUALS, Options.Multiplicity.ZERO_OR_ONE); // second input file name
		
		if (!opt.check(false, false)) {
			ErrorMessage.error("Error(s) in command line options:\n" + opt.getCheckErrors());
		}
		// settings file
		boolean settingsFilenameOption = false;
		String settingsFilename = DEFAULT__SETTINGS_FILENAME;
		if (opt.getSet().isSet("anchor")) {
			// react to option -anchor
			String anchorFilename = opt.getSet().getOption("anchor").getResultValue(0);
			File file = new File(anchorFilename);
			model.anchorWordList.loadFromFile(file);
		}

		if (opt.getSet().isSet("in1")) {
			// react to option -in1
			String in1Filename = opt.getSet().getOption("in1").getResultValue(0);
			File file = new File(in1Filename);
			model.loadTobeAlignedFile(file, 0);
		}

		if (opt.getSet().isSet("in2")) {
			// react to option -in2
			String in2Filename = opt.getSet().getOption("in2").getResultValue(0);
			File file = new File(in2Filename);
			model.loadTobeAlignedFile(file, 1);
		}
		

		if (opt.getSet().isSet("cli") && opt.getSet().isSet("cli-plain")) {
			System.err.println("Choose one of cli or cli-plain.");
			System.exit(1);
		}
		
		if (opt.getSet().isSet("cli")) {
			model.suggestWithoutGui();
			model.setAllCorrespAttributes();
			model.savePlain();
			model.saveXml();
		} else if (opt.getSet().isSet("cli-plain")) {
			model.suggestWithoutGui();
			model.setAllCorrespAttributes();
			model.savePlain();
		} else {
			gui = new AlignGui(model);

			if (opt.getSet().isSet("cfg")) {
				// react to option -cfg
				settingsFilename = opt.getSet().getOption("cfg").getResultValue(0);
				settingsFilenameOption = true;
				// read settings from file and store in model
				File f = new File(settingsFilename);
				if (f.exists()) {
					SettingsDialog sD = new SettingsDialog(null, gui);
					if (!sD.loadFile(f, "model")) {
						// error messages have been shown ########vil komme feilmeldinger også i lovlig tilfelle, når default fil ikke er der
						//...
					}
				} else {
					if (settingsFilenameOption) {
						ErrorMessage.error("Can't find the settings file specified in the -cfg option: " + settingsFilename);
					} // else the settings file was not specified in the command line arguments. the file that does not exist is the default settings file, and that is legal
				}
			}

			JFrame frame = new JFrame("TCA2");

			frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
			frame.getContentPane().add(gui);
			frame.setJMenuBar(gui.menuBar);
			// get the size of the default screen (¤¤¤in principle there can be more than one screen)
			Dimension screenDim = Toolkit.getDefaultToolkit().getScreenSize();

			frame.setSize(screenDim);
			frame.setVisible(true);
			frame.setLocationRelativeTo(null);   // relative to screen

			gui.compareInfoGraphics = gui.compareInfoPanel.getGraphics();
		}
	}
}

// <http://www.onjava.com/pub/a/onjava/2003/03/26/shutdownhook.html#listing1>
class ShutdownHook extends Thread {

	AlignmentModel model;

	ShutdownHook(AlignmentModel model) {
		super();
		this.model = model;
	}

    public void run() {
		if (model.logFileOut != null) {   // 2006-08-11
			try {
				String text = "\n\n>>> Program closed. Stop logging <<<\n\n";
				model.logFileOut.write(text, 0, text.length());
			} catch (Exception ex) {
				ErrorMessage.error("Exception when writing to " + model.getLogFilename() + ":\n" + ex.toString());
			}

			try {
				model.logFileOut.close();
			} catch (Exception e) {
				ErrorMessage.error("Exception when trying to close log file:\n" + e.toString());
			}
		}
    }
}
