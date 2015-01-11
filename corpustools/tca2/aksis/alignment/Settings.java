/*
 * Settings.java
 *
 * ...
 * ...
 * ...
 */

package aksis.alignment;

import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.border.*;
import java.io.*;
import java.nio.charset.Charset;

class SettingsDialog extends JDialog {

	boolean approved;   // ¤¤¤ er dette måten å returnere data på? kan ikke være private.

	//private int clusterScoreMethod;
	private int largeClusterScorePercentage;

	/*private int outputFileNamingMethod;*/

	private JButton okButton;   // close, with changes to settings
	private JButton cancelButton;   // close, with no changes to settings

	private JLabel relevantElementNamesLabel;
	private JTextField relevantElementNamesTextField;

	private JLabel relevantAncestorElementNamesLabel;
	private JTextField relevantAncestorElementNamesTextField;

	private JLabel specialCharactersLabel;
	private JTextField specialCharactersTextField;

	private JLabel scoringCharactersLabel;
	private JTextField scoringCharactersTextField;

	private JLabel lengthRatioLabel0;   // 2006-12-28
	private JLabel lengthRatioLabel1;
	private SpinnerNumberModel lengthRatioSpinnerNumberModel;
	private JSpinner lengthRatioSpinner;
	private JLabel lengthRatioLabel2;

	private JLabel diceMinWordLengthLabel;
	private SpinnerNumberModel diceMinWordLengthSpinnerNumberModel;
	private JSpinner diceMinWordLengthSpinner;

	private JLabel diceMinCountingScoreLabel;
	private SpinnerNumberModel diceMinCountingScoreSpinnerNumberModel;
	private JSpinner diceMinCountingScoreSpinner;

	private JButton loadButton;   // 2006-09-20b
	private JButton saveButton;   // 2006-09-20b

	/*
	private JLabel clusterScoreLabel;
	private JPanel clusterScorePanel;
	private ButtonGroup clusterScoreRadioGroup;
	private JRadioButton clusterScoreRadioButton1;
	private JRadioButton clusterScoreRadioButton2;
	private JRadioButton clusterScoreRadioButton3;
	*/
	private JLabel largeClusterScorePercentageLabel1;
	private JLabel largeClusterScorePercentageLabel2;
	private JLabel largeClusterScorePercentageLabel3;
	private SpinnerNumberModel largeClusterScorePercentageSpinnerNumberModel;
	private JSpinner largeClusterScorePercentageSpinner;

	private JPanel matchWeightPanel;
	private JLabel matchWeightLabel;
	private JLabel             anchorWordMatchWeightLabel;
	private SpinnerNumberModel anchorWordMatchWeightSpinnerNumberModel;
	private JSpinner           anchorWordMatchWeightSpinner;
	private JLabel             anchorPhraseMatchWeightLabel;
	private SpinnerNumberModel anchorPhraseMatchWeightSpinnerNumberModel;
	private JSpinner           anchorPhraseMatchWeightSpinner;
	private JLabel             properNameMatchWeightLabel;
	private SpinnerNumberModel properNameMatchWeightSpinnerNumberModel;
	private JSpinner           properNameMatchWeightSpinner;
	private JLabel             diceMatchWeightLabel;
	private SpinnerNumberModel diceMatchWeightSpinnerNumberModel;
	private JSpinner           diceMatchWeightSpinner;
	private JLabel             dicePhraseMatchWeightLabel;
	private SpinnerNumberModel dicePhraseMatchWeightSpinnerNumberModel;
	private JSpinner           dicePhraseMatchWeightSpinner;
	private JLabel             numberMatchWeightLabel;
	private SpinnerNumberModel numberMatchWeightSpinnerNumberModel;
	private JSpinner           numberMatchWeightSpinner;
	private JLabel             scoringCharacterMatchWeightLabel;
	private SpinnerNumberModel scoringCharacterMatchWeightSpinnerNumberModel;
	private JSpinner           scoringCharacterMatchWeightSpinner;

	/*
	private JLabel outputFileNamingLabel;
	private JPanel outputFileNamingPanel;
	private ButtonGroup outputFileNamingRadioGroup;
	private JRadioButton outputFileNamingRadioButton1;
	private JRadioButton outputFileNamingRadioButton2;
	//
	//private JPanel fileNamingExtensionPanel;
	private JLabel fileNamingExtensionLabel1;
	private JTextField fileNamingExtensionTextField1;
	private JLabel fileNamingExtensionLabel2;
	private JTextField fileNamingExtensionTextField2;
	//
	//private JPanel fileNamingSuffixPanel;
	private JLabel fileNamingSuffixLabel1;
	private JTextField fileNamingSuffixTextField1;
	private JLabel fileNamingSuffixLabel2;
	private JTextField fileNamingSuffixTextField2;
	*/

	//log//// 2006-02-23 match info log file

	//log//private JLabel logFileLabel;
	//log//private JTextField logFilenameTextField;

	private JLabel maxPathLengthLabel;
	private SpinnerNumberModel maxPathLengthSpinnerNumberModel;
	private JSpinner maxPathLengthSpinner;

	//private JPanel ancestorInfoPanel;
	private AncestorInfoRadioButtonPanel ancestorInfoRadioButtonPanel;
	private JLabel ancestorInfoElementNamesLabel;
	private JTextField ancestorInfoElementNamesTextField;
	private JLabel ancestorInfoAttributeNamesLabel;
	private JTextField ancestorInfoAttributeNamesTextField;

	//

    AlignmentModel model;    // package access
    AlignGui gui;   // 2006-09-21


    //public SettingsDialog(JFrame parent, AlignmentModel model) {
    public SettingsDialog(JFrame parent, AlignGui gui) {   // 2006-09-21

		//

		super(parent, "Settings dialog", true);

		//

        //this.model = model;
        this.gui = gui;   // 2006-09-21
        this.model = gui.model;   // 2006-09-21

		//

		OkAction okAction = new
			OkAction(
				"Accept changes to settings",
				createImageIcon("images/Select.gif", "'ticked' symbol"),
				"Accept changes to settings",
				new Integer(0)
			);

		CancelAction cancelAction = new
			CancelAction(
				"Cancel changes to settings",
				createImageIcon("images/Cancel.gif", "an X"),
				"Cancel changes to settings",
				new Integer(0)
			);

		// 2006-09-20b
		LoadAction loadAction = new
			LoadAction(
				"Load settings",
				createImageIcon("images/Read.gif", "read from disc"),
				"Load settings",
				new Integer(0)
			);

		SaveAction saveAction = new
			SaveAction(
				"Save settings",
				createImageIcon("images/Write.gif", "write to disc"),
				"Save settings",
				new Integer(0)
			);
		// end 2006-09-20b

		//

		//relevantElementNamesLabel = new JLabel("Relevant elements:");
		relevantElementNamesLabel = new JLabel("Alignable elements:");   // 2006-12-28
		relevantElementNamesTextField = new JTextField();
		relevantElementNamesTextField.setText(model.getRelevantElementNamesAsString());
		relevantElementNamesTextField.setFont(new Font("Courier New",Font.PLAIN, 16));

		//relevantAncestorElementNamesLabel = new JLabel("Relevant ancestors of relevant elements:");
		relevantAncestorElementNamesLabel = new JLabel("Ancestors of alignable elements:");   // 2006-12-28
		relevantAncestorElementNamesTextField = new JTextField();
		relevantAncestorElementNamesTextField.setText(model.getRelevantAncestorElementNamesAsString());
		relevantAncestorElementNamesTextField.setFont(new Font("Courier New",Font.PLAIN, 16));

		specialCharactersLabel = new JLabel("Special characters to be stripped from beginning and end of words:");
		specialCharactersTextField = new JTextField();
		specialCharactersTextField.setText(model.getSpecialCharacters());
		specialCharactersTextField.setFont(new Font("Courier New",Font.PLAIN, 16));

		scoringCharactersLabel = new JLabel("Special characters that add to the score:");
		scoringCharactersTextField = new JTextField();
		scoringCharactersTextField.setText(model.getScoringCharacters());
		scoringCharactersTextField.setFont(new Font("Courier New",Font.PLAIN, 16));

		//lengthRatioLabel1 = new JLabel("Sentences in text 2 are on the average");
		lengthRatioLabel0 = new JLabel("Content expressed in the language of text 2");   // 2006-12-28
		lengthRatioLabel1 = new JLabel("on the average needs");   // 2006-12-28
		Float lengthRatioSpinnerValue = new Float(model.getLengthRatio());
		Float lengthRatioSpinnerMin = new Float(Alignment.MIN__LENGTH_RATIO);
		Float lengthRatioSpinnerMax = new Float(Alignment.MAX__LENGTH_RATIO);
		Float lengthRatioSpinnerStep = new Float(Alignment.STEP__LENGTH_RATIO);
		lengthRatioSpinnerNumberModel = new SpinnerNumberModel(lengthRatioSpinnerValue, lengthRatioSpinnerMin, lengthRatioSpinnerMax, lengthRatioSpinnerStep);
		lengthRatioSpinner = new JSpinner(lengthRatioSpinnerNumberModel);
		//lengthRatioSpinner.setSize(new Dimension(100, 20));
		lengthRatioSpinner.setSize(new Dimension(30, 20));   // 2006-12-28
		//lengthRatioLabel2 = new JLabel("times as long as those in text 1");
		lengthRatioLabel2 = new JLabel("times as many characters as the same content expressed in the language of text 1");   // 2006-12-28

		diceMinWordLengthLabel = new JLabel("No Dice comparison on word with length less than");
		Integer diceMinWordLengthSpinnerValue = new Integer(model.getDiceMinWordLength());
		Integer diceMinWordLengthSpinnerMin = new Integer(Alignment.MIN__DICE_MIN_WORD_LENGTH);
		Integer diceMinWordLengthSpinnerMax = new Integer(100);
		Integer diceMinWordLengthSpinnerStep = new Integer(1);
		diceMinWordLengthSpinnerNumberModel = new SpinnerNumberModel(diceMinWordLengthSpinnerValue, diceMinWordLengthSpinnerMin, diceMinWordLengthSpinnerMax, diceMinWordLengthSpinnerStep);
		diceMinWordLengthSpinner = new JSpinner(diceMinWordLengthSpinnerNumberModel);
		//diceMinWordLengthSpinner.setPreferredSize(new Dimension(20, diceMinWordLengthSpinner.getPreferredSize().height));
		//diceMinWordLengthSpinner.setSize(new Dimension(100, 20));
		diceMinWordLengthSpinner.setSize(new Dimension(30, 20));   // 2006-12-28
		diceMinCountingScoreLabel = new JLabel("Raw Dice score must be at least");
		Float diceMinCountingScoreSpinnerValue = new Float(model.getDiceMinCountingScore());
		Float diceMinCountingScoreSpinnerMin = new Float(Alignment.MIN__DICE_MIN_COUNTING_SCORE);
		Float diceMinCountingScoreSpinnerMax = new Float(Alignment.MAX__DICE_MIN_COUNTING_SCORE);
		Float diceMinCountingScoreSpinnerStep = new Float(Alignment.STEP__DICE_MIN_COUNTING_SCORE);
		diceMinCountingScoreSpinnerNumberModel = new SpinnerNumberModel(diceMinCountingScoreSpinnerValue, diceMinCountingScoreSpinnerMin, diceMinCountingScoreSpinnerMax, diceMinCountingScoreSpinnerStep);
		diceMinCountingScoreSpinner = new JSpinner(diceMinCountingScoreSpinnerNumberModel);
		//diceMinCountingScoreSpinner.setPreferredSize(new Dimension(20, diceMinCountingScoreSpinner.getPreferredSize().height));
		//diceMinCountingScoreSpinner.setSize(new Dimension(100, 20));
		diceMinCountingScoreSpinner.setSize(new Dimension(30, 20));   // 2006-12-28

		maxPathLengthLabel = new JLabel("Number of steps to look ahead:");
		Integer maxPathLengthSpinnerValue = new Integer(model.getMaxPathLength());
		Integer maxPathLengthSpinnerMin = new Integer(1);
		Integer maxPathLengthSpinnerMax = new Integer(Alignment.MAX__MAX_PATH_LENGTH);
		Integer maxPathLengthSpinnerStep = new Integer(1);
		maxPathLengthSpinnerNumberModel = new SpinnerNumberModel(maxPathLengthSpinnerValue, maxPathLengthSpinnerMin, maxPathLengthSpinnerMax, maxPathLengthSpinnerStep);
		maxPathLengthSpinner = new JSpinner(maxPathLengthSpinnerNumberModel);
		//maxPathLengthSpinner.setPreferredSize(new Dimension(20, maxPathLengthSpinner.getPreferredSize().height));
		//maxPathLengthSpinner.setSize(new Dimension(100, 20));
		maxPathLengthSpinner.setSize(new Dimension(30, 20));   // 2006-12-28

		/*
		clusterScoreLabel = new JLabel("If 3 words in one text match 2 words in the other text, the score is");
		clusterScorePanel = new JPanel();
		clusterScoreRadioGroup = new ButtonGroup();
		*/
		//largeClusterScorePercentageLabel1 = new JLabel("### Extra score for additional words in clusters from word based methods");
		largeClusterScorePercentageLabel1 = new JLabel("If e.g. 4 words in one text match 3 words in the other,");
		largeClusterScorePercentageLabel2 = new JLabel("the 2 extra words in the smaller set of 3 words score");
		largeClusterScorePercentageLabel3 = new JLabel("% extra each");
		//
		//clusterScoreMethod = model.getClusterScoreMethod();
		//largeClusterScorePercentage = model.getLargeClusterScorePercentage();
		//
		/*
		clusterScoreRadioButton1 = new JRadioButton("1");
		clusterScoreRadioButton1.setMnemonic(KeyEvent.VK_1);   // set key accelerator
		clusterScoreRadioButton1.setSelected(clusterScoreMethod == 1);
		clusterScorePanel.add(clusterScoreRadioButton1);   // add to gui
		clusterScoreRadioGroup.add(clusterScoreRadioButton1);   // include in group
		//
		clusterScoreRadioButton2 = new JRadioButton("2");
		clusterScoreRadioButton2.setMnemonic(KeyEvent.VK_2);   // set key accelerator
		clusterScoreRadioButton2.setSelected(clusterScoreMethod == 2);
		clusterScorePanel.add(clusterScoreRadioButton2);   // add to gui
		clusterScoreRadioGroup.add(clusterScoreRadioButton2);   // include in group
		//
		clusterScoreRadioButton3 = new JRadioButton("3");
		clusterScoreRadioButton3.setMnemonic(KeyEvent.VK_3);   // set key accelerator
		clusterScoreRadioButton3.setSelected(clusterScoreMethod == 3);
		clusterScorePanel.add(clusterScoreRadioButton3);   // add to gui
		clusterScoreRadioGroup.add(clusterScoreRadioButton3);   // include in group
		*/
		Integer largeClusterScorePercentageSpinnerValue = new Integer(model.getLargeClusterScorePercentage());
		Integer largeClusterScorePercentageSpinnerMin = new Integer(Alignment.MIN__LARGE_CLUSTER_SCORE_PERCENTAGE);
		Integer largeClusterScorePercentageSpinnerMax = new Integer(Alignment.MAX__LARGE_CLUSTER_SCORE_PERCENTAGE);
		Integer largeClusterScorePercentageSpinnerStep = new Integer(Alignment.STEP__LARGE_CLUSTER_SCORE_PERCENTAGE);
		largeClusterScorePercentageSpinnerNumberModel = new SpinnerNumberModel(largeClusterScorePercentageSpinnerValue, largeClusterScorePercentageSpinnerMin, largeClusterScorePercentageSpinnerMax, largeClusterScorePercentageSpinnerStep);
		largeClusterScorePercentageSpinner = new JSpinner(largeClusterScorePercentageSpinnerNumberModel);
		//largeClusterScorePercentageSpinner.setSize(new Dimension(50, 20));
		largeClusterScorePercentageSpinner.setSize(new Dimension(30, 20));   // 2006-12-28

		//

		matchWeightPanel = new JPanel();
		matchWeightLabel = new JLabel("Weights");

		anchorWordMatchWeightLabel       = new JLabel("Anchor word");
		anchorPhraseMatchWeightLabel     = new JLabel("Anchor phrase");
		properNameMatchWeightLabel       = new JLabel("Proper name");
		diceMatchWeightLabel             = new JLabel("Dice word");
		dicePhraseMatchWeightLabel       = new JLabel("Dice phrase");
		numberMatchWeightLabel           = new JLabel("Number");
		scoringCharacterMatchWeightLabel = new JLabel("Special char");

		// smaller font to save space
		Font labelFont = matchWeightLabel.getFont().deriveFont(10.0f);
		anchorWordMatchWeightLabel.setFont(labelFont);
		anchorPhraseMatchWeightLabel.setFont(labelFont);
		properNameMatchWeightLabel.setFont(labelFont);
		diceMatchWeightLabel.setFont(labelFont);
		dicePhraseMatchWeightLabel.setFont(labelFont);
		numberMatchWeightLabel.setFont(labelFont);
		scoringCharacterMatchWeightLabel.setFont(labelFont);

		Float anchorWordMatchWeightSpinnerValue = new Float(model.getAnchorWordMatchWeight());
		Float anchorWordMatchWeightSpinnerMin = new Float(Alignment.MIN__ANCHORWORD_MATCH_WEIGHT);
		Float anchorWordMatchWeightSpinnerMax = new Float(Alignment.MAX__ANCHORWORD_MATCH_WEIGHT);
		Float anchorWordMatchWeightSpinnerStep = new Float(Alignment.STEP__MATCH_WEIGHT);
		anchorWordMatchWeightSpinnerNumberModel = new SpinnerNumberModel(anchorWordMatchWeightSpinnerValue, anchorWordMatchWeightSpinnerMin, anchorWordMatchWeightSpinnerMax, anchorWordMatchWeightSpinnerStep);
		anchorWordMatchWeightSpinner = new JSpinner(anchorWordMatchWeightSpinnerNumberModel);
		anchorWordMatchWeightSpinner.setSize(new Dimension(30, 20));

		Float anchorPhraseMatchWeightSpinnerValue = new Float(model.getAnchorPhraseMatchWeight());
		Float anchorPhraseMatchWeightSpinnerMin = new Float(Alignment.MIN__ANCHORPHRASE_MATCH_WEIGHT);
		Float anchorPhraseMatchWeightSpinnerMax = new Float(Alignment.MAX__ANCHORPHRASE_MATCH_WEIGHT);
		Float anchorPhraseMatchWeightSpinnerStep = new Float(Alignment.STEP__MATCH_WEIGHT);
		anchorPhraseMatchWeightSpinnerNumberModel = new SpinnerNumberModel(anchorPhraseMatchWeightSpinnerValue, anchorPhraseMatchWeightSpinnerMin, anchorPhraseMatchWeightSpinnerMax, anchorPhraseMatchWeightSpinnerStep);
		anchorPhraseMatchWeightSpinner = new JSpinner(anchorPhraseMatchWeightSpinnerNumberModel);
		anchorPhraseMatchWeightSpinner.setSize(new Dimension(30, 20));

		Float properNameMatchWeightSpinnerValue = new Float(model.getProperNameMatchWeight());
		Float properNameMatchWeightSpinnerMin = new Float(Alignment.MIN__PROPERNAME_MATCH_WEIGHT);
		Float properNameMatchWeightSpinnerMax = new Float(Alignment.MAX__PROPERNAME_MATCH_WEIGHT);
		Float properNameMatchWeightSpinnerStep = new Float(Alignment.STEP__MATCH_WEIGHT);
		properNameMatchWeightSpinnerNumberModel = new SpinnerNumberModel(properNameMatchWeightSpinnerValue, properNameMatchWeightSpinnerMin, properNameMatchWeightSpinnerMax, properNameMatchWeightSpinnerStep);
		properNameMatchWeightSpinner = new JSpinner(properNameMatchWeightSpinnerNumberModel);
		properNameMatchWeightSpinner.setSize(new Dimension(30, 20));

		Float diceMatchWeightSpinnerValue = new Float(model.getDiceMatchWeight());
		Float diceMatchWeightSpinnerMin = new Float(Alignment.MIN__DICE_MATCH_WEIGHT);
		Float diceMatchWeightSpinnerMax = new Float(Alignment.MAX__DICE_MATCH_WEIGHT);
		Float diceMatchWeightSpinnerStep = new Float(Alignment.STEP__MATCH_WEIGHT);
		diceMatchWeightSpinnerNumberModel = new SpinnerNumberModel(diceMatchWeightSpinnerValue, diceMatchWeightSpinnerMin, diceMatchWeightSpinnerMax, diceMatchWeightSpinnerStep);
		diceMatchWeightSpinner = new JSpinner(diceMatchWeightSpinnerNumberModel);
		diceMatchWeightSpinner.setSize(new Dimension(30, 20));

		Float dicePhraseMatchWeightSpinnerValue = new Float(model.getDicePhraseMatchWeight());
		Float dicePhraseMatchWeightSpinnerMin = new Float(Alignment.MIN__DICEPHRASE_MATCH_WEIGHT);
		Float dicePhraseMatchWeightSpinnerMax = new Float(Alignment.MAX__DICEPHRASE_MATCH_WEIGHT);
		Float dicePhraseMatchWeightSpinnerStep = new Float(Alignment.STEP__MATCH_WEIGHT);
		dicePhraseMatchWeightSpinnerNumberModel = new SpinnerNumberModel(dicePhraseMatchWeightSpinnerValue, dicePhraseMatchWeightSpinnerMin, dicePhraseMatchWeightSpinnerMax, dicePhraseMatchWeightSpinnerStep);
		dicePhraseMatchWeightSpinner = new JSpinner(dicePhraseMatchWeightSpinnerNumberModel);
		dicePhraseMatchWeightSpinner.setSize(new Dimension(30, 20));

		Float numberMatchWeightSpinnerValue = new Float(model.getNumberMatchWeight());
		Float numberMatchWeightSpinnerMin = new Float(Alignment.MIN__NUMBER_MATCH_WEIGHT);
		Float numberMatchWeightSpinnerMax = new Float(Alignment.MAX__NUMBER_MATCH_WEIGHT);
		Float numberMatchWeightSpinnerStep = new Float(Alignment.STEP__MATCH_WEIGHT);
		numberMatchWeightSpinnerNumberModel = new SpinnerNumberModel(numberMatchWeightSpinnerValue, numberMatchWeightSpinnerMin, numberMatchWeightSpinnerMax, numberMatchWeightSpinnerStep);
		numberMatchWeightSpinner = new JSpinner(numberMatchWeightSpinnerNumberModel);
		numberMatchWeightSpinner.setSize(new Dimension(30, 20));

		Float scoringCharacterMatchWeightSpinnerValue = new Float(model.getScoringCharacterMatchWeight());
		Float scoringCharacterMatchWeightSpinnerMin = new Float(Alignment.MIN__SCORINGCHARACTER_MATCH_WEIGHT);
		Float scoringCharacterMatchWeightSpinnerMax = new Float(Alignment.MAX__SCORINGCHARACTER_MATCH_WEIGHT);
		Float scoringCharacterMatchWeightSpinnerStep = new Float(Alignment.STEP__MATCH_WEIGHT);
		scoringCharacterMatchWeightSpinnerNumberModel = new SpinnerNumberModel(scoringCharacterMatchWeightSpinnerValue, scoringCharacterMatchWeightSpinnerMin, scoringCharacterMatchWeightSpinnerMax, scoringCharacterMatchWeightSpinnerStep);
		scoringCharacterMatchWeightSpinner = new JSpinner(scoringCharacterMatchWeightSpinnerNumberModel);
		scoringCharacterMatchWeightSpinner.setSize(new Dimension(30, 20));

		//

		/*
		outputFileNamingLabel = new JLabel("Suggest output file names with a");
		outputFileNamingPanel = new JPanel();
		outputFileNamingRadioGroup = new ButtonGroup();
		//
		outputFileNamingMethod = model.getOutputFileNamingMethod();
		//
		outputFileNamingRadioButton1 = new JRadioButton("different extension");
		outputFileNamingRadioButton1.setMnemonic(KeyEvent.VK_E);   // set key accelerator
		outputFileNamingRadioButton1.setSelected(outputFileNamingMethod == 1);   // ####
		outputFileNamingPanel.add(outputFileNamingRadioButton1);   // add to gui
		outputFileNamingRadioGroup.add(outputFileNamingRadioButton1);   // include in group
		//
		outputFileNamingRadioButton2 = new JRadioButton("suffix");
		outputFileNamingRadioButton2.setMnemonic(KeyEvent.VK_S);   // set key accelerator
		outputFileNamingRadioButton2.setSelected(outputFileNamingMethod == 2);   // ####
		outputFileNamingPanel.add(outputFileNamingRadioButton2);   // add to gui
		outputFileNamingRadioGroup.add(outputFileNamingRadioButton2);   // include in group
		//
		//fileNamingExtensionPanel = new JPanel();
		fileNamingExtensionLabel1 = new JLabel("Extension for 'corresp' format:");
		fileNamingExtensionTextField1 = new JTextField();
		fileNamingExtensionTextField1.setText(model.getFileNamingCorrespExtension());
		fileNamingExtensionTextField1.setFont(new Font("Courier New",Font.PLAIN, 16));
		fileNamingExtensionLabel2 = new JLabel("Extension for 'newline' format:");
		fileNamingExtensionTextField2 = new JTextField();
		fileNamingExtensionTextField2.setText(model.getFileNamingNewlineExtension());
		fileNamingExtensionTextField2.setFont(new Font("Courier New",Font.PLAIN, 16));
		//
		//fileNamingSuffixPanel = new JPanel();
		fileNamingSuffixLabel1 = new JLabel("Suffix for 'corresp' format:");
		fileNamingSuffixTextField1 = new JTextField();
		fileNamingSuffixTextField1.setText(model.getFileNamingCorrespSuffix());
		fileNamingSuffixTextField1.setFont(new Font("Courier New",Font.PLAIN, 16));
		fileNamingSuffixLabel2 = new JLabel("Suffix for 'newline' format:");
		fileNamingSuffixTextField2 = new JTextField();
		fileNamingSuffixTextField2.setText(model.getFileNamingNewlineSuffix());
		fileNamingSuffixTextField2.setFont(new Font("Courier New",Font.PLAIN, 16));
		*/

		//ancestorInfoPanel = new JPanel();

		ancestorInfoRadioButtonPanel = new AncestorInfoRadioButtonPanel(model.getAncestorInfoChoice(), this.getBackground());
		ancestorInfoElementNamesLabel = new JLabel("Element names:");
		ancestorInfoElementNamesTextField = new JTextField(model.getAncestorInfoElementNamesAsString());
		ancestorInfoElementNamesTextField.setFont(new Font("Courier New",Font.PLAIN, 16));
		ancestorInfoAttributeNamesLabel = new JLabel("Attribute names:");
		ancestorInfoAttributeNamesTextField = new JTextField(model.getAncestorInfoAttributeNamesAsString());
		ancestorInfoAttributeNamesTextField.setFont(new Font("Courier New",Font.PLAIN, 16));

		//log//// 2006-02-23 match info log file
		//log//logFileLabel = new JLabel("Log file");
		//log//logFilenameTextField = new JTextField();
		//log//logFilenameTextField.setText(model.getLogFilename());

		okButton = new JButton(okAction);
		okButton.setName("O");   // ¤¤¤ husker ikke om dette kan brukes til noe

		cancelButton = new JButton(cancelAction);
		cancelButton.setName("C");   // ¤¤¤ husker ikke om dette kan brukes til noe

		// 2006-09-20b
		loadButton = new JButton(loadAction);
		loadButton.setName("L");   // ¤¤¤ husker ikke om dette kan brukes til noe

		saveButton = new JButton(saveAction);
		saveButton.setName("S");   // ¤¤¤ husker ikke om dette kan brukes til noe
		// end 2006-09-20b

		//

        //Container cp = new Container();
        //cp = getContentPane();
        GridBagLayout layout = new GridBagLayout();
        //cp.setLayout(layout);
        JPanel cp = new JPanel(layout);
        GridBagConstraints c = new GridBagConstraints();
        c.insets = new Insets(3,3,3,3);
        AwtUtil util = new AwtUtil(cp, layout, c);

		//

		/*
		try {
			//URL url = new URL("http://today.java.net/jag/bio/JagHeadshot-small.jpg");
			//URL url = new URL("http://www.aksis.uib.no/people/images/16.jpg");
			//URL url = new URL("http://www.backgroundsarchive.com/images/pub/4/4511lugiz3wwm9.jpg");
			URL url = new URL("http://www.swapmeetdave.com/Humor/Cats/Kitten-Duck.jpg");
			try {
				BufferedImage image = ImageIO.read(url);
				//cp.setPreferredSize(new Dimension(image.getWidth(), image.getHeight()));
				cp.setBorder(new CentredBackgroundBorder(image));
			} catch(IOException e) {
				System.out.println("Oops " + e);
				//cp.setPreferredSize(new Dimension(400, 400));
			}
		} catch (MalformedURLException e) {
			System.out.println("Oops " + e);
			//cp.setPreferredSize(new Dimension(400, 400));
		}
		*/

        //

        Box b;

		c.gridy = 0;   // ###############

        // load/save buttons

		c.gridy++;   // ###############
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;

		b = new Box(BoxLayout.X_AXIS);
		b.add(loadButton);
		b.add(Box.createHorizontalGlue());
		b.add(saveButton);

		util.addInGridBag(b);

		// relevant elements
		// = alignable elements // 2006-12-28

		c.gridy++;   // ###############
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;

		Box relevantElementNamesBox = new Box(BoxLayout.X_AXIS);
		relevantElementNamesBox.add(Box.createHorizontalGlue());
		relevantElementNamesBox.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset
		relevantElementNamesBox.add(relevantElementNamesLabel);
		relevantElementNamesBox.add(Box.createHorizontalStrut(10));
		relevantElementNamesBox.add(relevantElementNamesTextField);
		relevantElementNamesBox.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset

		Box relevantAncestorElementNamesBox = new Box(BoxLayout.X_AXIS);
		relevantAncestorElementNamesBox.add(Box.createHorizontalGlue());
		relevantAncestorElementNamesBox.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset
		relevantAncestorElementNamesBox.add(relevantAncestorElementNamesLabel);
		relevantAncestorElementNamesBox.add(Box.createHorizontalStrut(10));
		relevantAncestorElementNamesBox.add(relevantAncestorElementNamesTextField);
		relevantAncestorElementNamesBox.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset

		b = new Box(BoxLayout.Y_AXIS);
		b.add(Box.createVerticalStrut(5));   // ###clunky way of doing inset
		b.add(relevantElementNamesBox);
		b.add(relevantAncestorElementNamesBox);
		b.add(Box.createVerticalStrut(5));   // ###clunky way of doing inset
		b.setBorder(new BevelBorder(BevelBorder.LOWERED));

		util.addInGridBag(b);

        // special characters

		c.gridy++;   // ###############
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;

		b = new Box(BoxLayout.Y_AXIS);
		b.add(specialCharactersLabel);
		b.add(specialCharactersTextField);

		util.addInGridBag(b);

		// score-giving characters

		c.gridy++;   // ###############
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;

		b = new Box(BoxLayout.Y_AXIS);
		b.add(scoringCharactersLabel);
		b.add(scoringCharactersTextField);

		util.addInGridBag(b);

		// length ratio

		c.gridy++;   // ###############
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;

		Box lengthRatioBox1 = new Box(BoxLayout.X_AXIS);   // 2006-12-28
		lengthRatioBox1.add(Box.createHorizontalStrut(5));   // 2006-12-28   // ###clunky way of doing inset
		lengthRatioBox1.add(lengthRatioLabel0);   // 2006-12-28
		lengthRatioBox1.add(Box.createHorizontalGlue());   // 2006-12-28

		//b = new Box(BoxLayout.X_AXIS);
		//b.add(Box.createHorizontalGlue());
		//b.add(lengthRatioLabel1);
		//b.add(Box.createHorizontalStrut(10));
		//b.add(lengthRatioSpinner);
		//b.add(Box.createHorizontalStrut(10));
		//b.add(lengthRatioLabel2);
		Box lengthRatioBox2 = new Box(BoxLayout.X_AXIS);   // 2006-12-28
		lengthRatioBox2.add(Box.createHorizontalStrut(5));   // 2006-12-28   // ###clunky way of doing inset
		lengthRatioBox2.add(lengthRatioLabel1);   // 2006-12-28
		lengthRatioBox2.add(Box.createHorizontalStrut(10));   // 2006-12-28
		lengthRatioBox2.add(lengthRatioSpinner);   // 2006-12-28
		lengthRatioBox2.add(Box.createHorizontalStrut(10));   // 2006-12-28
		lengthRatioBox2.add(lengthRatioLabel2);   // 2006-12-28
		lengthRatioBox2.add(Box.createHorizontalStrut(5));   // 2006-12-28   // ###clunky way of doing inset

		b = new Box(BoxLayout.Y_AXIS);
		b.add(Box.createVerticalStrut(5));   // 2006-12-28
		b.add(lengthRatioBox1);   // 2006-12-28
		b.add(lengthRatioBox2);   // 2006-12-28
		b.setBorder(new BevelBorder(BevelBorder.LOWERED));   // 2006-12-28

		util.addInGridBag(b);

		// dice settings

		c.gridy++;   // ###############
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;

		Box diceMinWordlengthBox = new Box(BoxLayout.X_AXIS);
		diceMinWordlengthBox.add(Box.createHorizontalGlue());
		diceMinWordlengthBox.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset
		diceMinWordlengthBox.add(diceMinWordLengthLabel);
		diceMinWordlengthBox.add(Box.createHorizontalStrut(10));
		diceMinWordlengthBox.add(diceMinWordLengthSpinner);
		diceMinWordlengthBox.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset

		Box diceMinCountingScore = new Box(BoxLayout.X_AXIS);
		diceMinCountingScore.add(Box.createHorizontalGlue());
		diceMinCountingScore.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset
		diceMinCountingScore.add(diceMinCountingScoreLabel);
		diceMinCountingScore.add(Box.createHorizontalStrut(10));
		diceMinCountingScore.add(diceMinCountingScoreSpinner);
		diceMinCountingScore.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset

		b = new Box(BoxLayout.Y_AXIS);
		b.add(Box.createVerticalStrut(5));   // ###clunky way of doing inset
		b.add(diceMinWordlengthBox);
		b.add(diceMinCountingScore);
		b.add(Box.createVerticalStrut(5));   // ###clunky way of doing inset
		b.setBorder(new BevelBorder(BevelBorder.LOWERED));

		util.addInGridBag(b);

		// 'large cluster' settings

		c.gridy++;   // ###############
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;

		Box b1 = new Box(BoxLayout.X_AXIS);
		b1.add(Box.createHorizontalStrut(10));   // 2006-12-28
		b1.add(largeClusterScorePercentageLabel1);
		b1.add(Box.createHorizontalGlue());

		Box b2 = new Box(BoxLayout.X_AXIS);
		b2.add(Box.createHorizontalStrut(10));   // 2006-12-28
		b2.add(largeClusterScorePercentageLabel2);
		b2.add(Box.createHorizontalStrut(10));
		b2.add(largeClusterScorePercentageSpinner);
		b2.add(Box.createHorizontalStrut(10));
		b2.add(largeClusterScorePercentageLabel3);
		b2.add(Box.createHorizontalGlue());

		b = new Box(BoxLayout.Y_AXIS);

		b.add(Box.createVerticalStrut(5));
		b.add(b1);
		b.add(b2);
		b.add(Box.createVerticalStrut(5));

		//b.add(clusterScoreLabel);
		//b.add(clusterScorePanel);

		util.addInGridBag(b);

		// weights

		c.gridy++;   // ###############
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;

		// ### denne har labler og spinnere for enkeltvektene, men ikke hovedoverskriften
		matchWeightPanel.setLayout(new GridLayout(2, 7, 5, 0));

		matchWeightPanel.add(anchorWordMatchWeightLabel);
		matchWeightPanel.add(anchorPhraseMatchWeightLabel);
		matchWeightPanel.add(properNameMatchWeightLabel);
		matchWeightPanel.add(diceMatchWeightLabel);
		matchWeightPanel.add(dicePhraseMatchWeightLabel);
		matchWeightPanel.add(numberMatchWeightLabel);
		matchWeightPanel.add(scoringCharacterMatchWeightLabel);
		matchWeightPanel.add(anchorWordMatchWeightSpinner);
		matchWeightPanel.add(anchorPhraseMatchWeightSpinner);
		matchWeightPanel.add(properNameMatchWeightSpinner);
		matchWeightPanel.add(diceMatchWeightSpinner);
		matchWeightPanel.add(dicePhraseMatchWeightSpinner);
		matchWeightPanel.add(numberMatchWeightSpinner);
		matchWeightPanel.add(scoringCharacterMatchWeightSpinner);

		// ### denne ...
		Box matchWeightBox = new Box(BoxLayout.Y_AXIS);
		matchWeightBox.add(Box.createVerticalStrut(5));   // ###clunky way of doing inset
		matchWeightBox.add(matchWeightLabel);
		matchWeightBox.add(matchWeightPanel);
		matchWeightBox.add(Box.createVerticalStrut(5));   // ###clunky way of doing inset

		Box outerMatchWeightBox = new Box(BoxLayout.X_AXIS);   // 2006-12-28
		outerMatchWeightBox.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset      // 2006-12-28
		outerMatchWeightBox.add(matchWeightBox);   // 2006-12-28

		//matchWeightBox.setBorder(new BevelBorder(BevelBorder.LOWERED));
		outerMatchWeightBox.setBorder(new BevelBorder(BevelBorder.LOWERED));   // 2006-12-28

		//util.addInGridBag(matchWeightBox);
		util.addInGridBag(outerMatchWeightBox);   // 2006-12-28

        // path length

		c.gridy++;   // ###############
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;

		b = new Box(BoxLayout.X_AXIS);
		b.add(Box.createHorizontalGlue());
		b.add(maxPathLengthLabel);
		b.add(Box.createHorizontalStrut(10));
		b.add(maxPathLengthSpinner);
		b.add(Box.createHorizontalStrut(10));   // 2006-12-28

		util.addInGridBag(b);

		/*
		// output file naming method

		c.gridy++;   // ###############
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;

		Box fileNamingMethodBox = new Box(BoxLayout.X_AXIS);
		fileNamingMethodBox.add(Box.createHorizontalGlue());
		fileNamingMethodBox.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset
		fileNamingMethodBox.add(outputFileNamingLabel);
		//fileNamingMethodBox.add(Box.createHorizontalStrut(10));
		fileNamingMethodBox.add(outputFileNamingPanel);
		fileNamingMethodBox.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset
		fileNamingMethodBox.add(Box.createHorizontalGlue());

		Box extensionBox = new Box(BoxLayout.X_AXIS);
		extensionBox.add(Box.createHorizontalGlue());
		extensionBox.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset
		extensionBox.add(fileNamingExtensionLabel1);
		extensionBox.add(Box.createHorizontalStrut(10));
		extensionBox.add(fileNamingExtensionTextField1);
		extensionBox.add(Box.createHorizontalStrut(20));
		extensionBox.add(fileNamingExtensionLabel2);
		extensionBox.add(Box.createHorizontalStrut(10));
		extensionBox.add(fileNamingExtensionTextField2);
		extensionBox.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset
		extensionBox.add(Box.createHorizontalGlue());

		Box suffixBox = new Box(BoxLayout.X_AXIS);
		suffixBox.add(Box.createHorizontalGlue());
		suffixBox.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset
		suffixBox.add(fileNamingSuffixLabel1);
		suffixBox.add(Box.createHorizontalStrut(10));
		suffixBox.add(fileNamingSuffixTextField1);
		suffixBox.add(Box.createHorizontalStrut(20));
		suffixBox.add(fileNamingSuffixLabel2);
		suffixBox.add(Box.createHorizontalStrut(10));
		suffixBox.add(fileNamingSuffixTextField2);
		suffixBox.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset
		suffixBox.add(Box.createHorizontalGlue());

		b = new Box(BoxLayout.Y_AXIS);
		b.add(Box.createVerticalStrut(5));   // ###clunky way of doing inset
		b.add(fileNamingMethodBox);
		//b.add(extensionFileNamingPanel);
		b.add(extensionBox);
		//b.add(suffixFileNamingPanel);
		b.add(suffixBox);
		b.add(Box.createVerticalStrut(5));   // ###clunky way of doing inset
		b.setBorder(new BevelBorder(BevelBorder.LOWERED));

		util.addInGridBag(b);
		*/

		// newline format ancestor info

		c.gridy++;   // ###############
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;

		Box ancestorInfoElementNamesBox = new Box(BoxLayout.X_AXIS);
		ancestorInfoElementNamesBox.add(Box.createHorizontalGlue());
		ancestorInfoElementNamesBox.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset
		ancestorInfoElementNamesBox.add(ancestorInfoElementNamesLabel);
		ancestorInfoElementNamesBox.add(Box.createHorizontalStrut(10));
		ancestorInfoElementNamesBox.add(ancestorInfoElementNamesTextField);
		ancestorInfoElementNamesBox.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset

		Box ancestorInfoAttributeNamesBox = new Box(BoxLayout.X_AXIS);
		ancestorInfoAttributeNamesBox.add(Box.createHorizontalGlue());
		ancestorInfoAttributeNamesBox.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset
		ancestorInfoAttributeNamesBox.add(ancestorInfoAttributeNamesLabel);
		ancestorInfoAttributeNamesBox.add(Box.createHorizontalStrut(10));
		ancestorInfoAttributeNamesBox.add(ancestorInfoAttributeNamesTextField);
		ancestorInfoAttributeNamesBox.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset

		b = new Box(BoxLayout.Y_AXIS);
		b.add(Box.createVerticalStrut(5));   // ###clunky way of doing inset
		b.add(ancestorInfoRadioButtonPanel);
		//b.add(ancestorInfoElementNamesLabel);
		//b.add(ancestorInfoElementNamesTextField);
		b.add(ancestorInfoElementNamesBox);
		//b.add(ancestorInfoAttributeNamesLabel);
		//b.add(ancestorInfoAttributeNamesTextField);
		b.add(ancestorInfoAttributeNamesBox);
		b.add(Box.createVerticalStrut(5));   // ###clunky way of doing inset
		b.setBorder(new BevelBorder(BevelBorder.LOWERED));

		util.addInGridBag(b);

		//log//// 2006-02-23 match info log file
		//log//// log file
		//log//
		//log//c.gridy++;   // ###############
		//log//c.weighty = 1;
		//log//c.gridx = 0;
		//log//c.gridwidth = 1;
		//log//c.weightx = 0;
		//log//c.fill = GridBagConstraints.HORIZONTAL;
		//log//
		//log//b = new Box(BoxLayout.X_AXIS);
		//log//b.add(Box.createHorizontalGlue());
		//log//b.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset
		//log//b.add(logFileLabel);
		//log//b.add(Box.createHorizontalStrut(10));
		//log//b.add(logFilenameTextField);
		//log//b.add(Box.createHorizontalStrut(5));   // ###clunky way of doing inset
		//log//
		//log//util.addInGridBag(b);

		// (space)

		c.gridy++;   // ###############
		c.weighty = 10;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.BOTH;

        // ok/cancel buttons

		c.gridy++;   // ###############
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;

		b = new Box(BoxLayout.X_AXIS);
		b.add(okButton);
		b.add(Box.createHorizontalGlue());
		b.add(cancelButton);

		util.addInGridBag(b);

		// ...

		okButton.setMnemonic(KeyEvent.VK_O);   // Ok
		cancelButton.setMnemonic(KeyEvent.VK_C);   // Cancel

		// tool tip

		maxPathLengthSpinner.setToolTipText("Set length of paths to explore, measured in alignments");
		okButton.setToolTipText("Accept changes to settings");
		cancelButton.setToolTipText("Cancel changes to settings");

		//

		//// ### ooops. endrer direkte. ingen angremulighet
		//maxPathLengthSpinner.addChangeListener(new ChangeListener() {
		//	public void stateChanged(ChangeEvent e) {
		//		model.maxPathLength = maxPathLengthSpinner.getNumber().intValue();
		//	}
		//});

		//

		this.setContentPane(cp);

		//setSize(600, 600);
		setSize(600, 750);   // 2006-12-28

	}

	// §§§ skulle denne vært gjenbrukt? er i både AlignGui og Settings og her
	public abstract class MyAbstractAction extends AbstractAction {
		public MyAbstractAction(String text, ImageIcon icon, String desc, Integer mnemonic) {
			super(text, icon);
			putValue(SHORT_DESCRIPTION, desc);
			putValue(MNEMONIC_KEY, mnemonic);
		}
	}

	// 2006-09-20b, 2006-09-21
	public class LoadAction extends MyAbstractAction {
		public LoadAction(String text, ImageIcon icon, String desc, Integer mnemonic) {
			super(text, icon, desc, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {

			String command = e.getActionCommand();
			//System.out.println("command er " + command);

			JFileChooser chooser = new JFileChooser();
			chooser.setApproveButtonText("Load settings from file");
			if (model.currentOpenDirectory != null) {
				chooser.setCurrentDirectory(model.currentOpenDirectory);
			} else {
				chooser.setCurrentDirectory(null);
			}

			int returnVal = chooser.showOpenDialog(SettingsDialog.this);   // arg får open-dialog til å ligge sentrert over settings-dialog. hvis null havner open-dialog i senter av skjerm
			if(returnVal == JFileChooser.APPROVE_OPTION) {
				// (read value settings from file and display in dialog)
				if (loadFile(chooser.getSelectedFile(), "dialog")) {
					//...;   ¤¤¤
				} else {
					//...;   ¤¤¤
				}
				model.currentOpenDirectory = chooser.getCurrentDirectory();
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
			chooser.setApproveButtonText("Save settings to file");
			if (model.currentOpenDirectory != null) {
				chooser.setCurrentDirectory(model.currentOpenDirectory);
			} else {
				chooser.setCurrentDirectory(null);
			}

			int returnVal = chooser.showSaveDialog(SettingsDialog.this);   // arg får open-dialog til å ligge sentrert over settings-dialog. hvis null havner open-dialog i senter av skjerm
			if(returnVal == JFileChooser.APPROVE_OPTION) {

				File f = chooser.getSelectedFile();

				boolean doSave;
				if(f.exists()) {
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
						doSave = true;
					} else {
						// NO
						doSave = false;
					}
				} else {
					doSave = true;
				}

				if (doSave) {
					if (saveFile(f)) {
						//...;   ¤¤¤
					} else {
						//...;   ¤¤¤
					}
				}
			}

		}
	}
	// end 2006-09-20b

	public class OkAction extends MyAbstractAction {
		public OkAction(String text, ImageIcon icon, String desc, Integer mnemonic) {
			super(text, icon, desc, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {

			String command = e.getActionCommand();
			//System.out.println("command er " + command);

			//

			model.setRelevantElementNames(relevantElementNamesTextField.getText());
			model.setRelevantAncestorElementNames(relevantAncestorElementNamesTextField.getText());

			// ############# dangerous? must strip whitespace. must check for duplicates
			model.setSpecialCharacters(specialCharactersTextField.getText());

			model.setScoringCharacters(scoringCharactersTextField.getText());

			model.setLengthRatio(((Float)lengthRatioSpinner.getValue()).floatValue());

			model.setDiceMinWordLength(((Integer)diceMinWordLengthSpinner.getValue()).intValue());

			model.setDiceMinCountingScore(((Float)diceMinCountingScoreSpinner.getValue()).floatValue());

			// ### veldig uelegant
			/*
			if (clusterScoreRadioButton1.isSelected()) {
				clusterScoreMethod = 1;
			} else if (clusterScoreRadioButton2.isSelected()) {
				clusterScoreMethod = 2;
			} else {
				clusterScoreMethod = 3;
			}
			model.setClusterScoreMethod(clusterScoreMethod);
			*/
			model.setLargeClusterScorePercentage(((Integer)largeClusterScorePercentageSpinner.getValue()).intValue());

			model.setMatchWeights(
				((Float)anchorWordMatchWeightSpinner.getValue()).floatValue(),
				((Float)anchorPhraseMatchWeightSpinner.getValue()).floatValue(),
				((Float)properNameMatchWeightSpinner.getValue()).floatValue(),
				((Float)diceMatchWeightSpinner.getValue()).floatValue(),
				((Float)dicePhraseMatchWeightSpinner.getValue()).floatValue(),
				((Float)numberMatchWeightSpinner.getValue()).floatValue(),
				((Float)scoringCharacterMatchWeightSpinner.getValue()).floatValue()
			);

			model.setMaxPathLength(((Integer)maxPathLengthSpinner.getValue()).intValue());

			/*
			// ### veldig uelegant
			if (outputFileNamingRadioButton1.isSelected()) {
				outputFileNamingMethod = 1;   // extension
			} else {
				outputFileNamingMethod = 2;   // suffix
			}
			model.setOutputFileNamingMethod(outputFileNamingMethod);
			model.setFileNamingCorrespExtension(fileNamingExtensionTextField1.getText());
			model.setFileNamingNewlineExtension(fileNamingExtensionTextField2.getText());
			model.setFileNamingCorrespSuffix(fileNamingSuffixTextField1.getText());
			model.setFileNamingNewlineSuffix(fileNamingSuffixTextField2.getText());
			*/

			int c;
			try {
				c = ancestorInfoRadioButtonPanel.getChoice();
			} catch (AncestorInfoRadioException e2) {
				// program error ###
				ErrorMessage.programError("Error in ancestor info radio button group");
				c = AncestorInfoRadioButtonPanel.NONE;
			}

			model.setAncestorInfo(
				c,
				ancestorInfoElementNamesTextField.getText(),
				ancestorInfoAttributeNamesTextField.getText()
			);

			//log//// 2006-02-23 match info log file
			//log//model.setLogFilename(logFilenameTextField.getText());

			SettingsDialog.this.approved = true;

			//... lukk. hvordan??? hide() ???????????????????
			SettingsDialog.this.dispose();

		}
	}

	public class CancelAction extends MyAbstractAction {
		public CancelAction(String text, ImageIcon icon, String desc, Integer mnemonic) {
			super(text, icon, desc, mnemonic);
		}
		public void actionPerformed(ActionEvent e) {

			String command = e.getActionCommand();
			//System.out.println("command er " + command);

			SettingsDialog.this.approved = false;

			//... lukk. hvordan??? hide() ???????????????????
			SettingsDialog.this.dispose();   // ser ut til å funke

		}
	}

	// 2006-09-20b, 2006-09-21
	//private boolean loadFile(AlignmentModel model, File f) { ????????????
	//private boolean loadFile(File f, String target) {
	public boolean loadFile(File f, String target) {

		// target is "dialog" or "model".
		// "dialog" : the method is called from the settings dialog
		//            and the setting values read from the file
		//            should be displayed in the dialog.
		// "model"  : the method is called from the app starting up
		//            and the setting values read from the file
		//            should be stored to the appropriate variables
		//            in the AlignmentModel.

		//###this method doesn't return exception but false. perhaps it should

		//¤¤¤ advarselsdialogs her eller i kallende kode?

		//System.out.println("loadFile() er under implementering");

        try {

			String data = "";

			// (###se kommentarer tilsvarende sted i AnchorDialog)
			InputStream fIn = new FileInputStream(f);
			InputStream bIn = new BufferedInputStream(fIn);
			Charset cs = Charset.forName("UTF-8");
			InputStreamReader in = new InputStreamReader(bIn, cs);

			int iChar;
			while ((iChar = in.read()) != -1) {
				data += ("" + (char)iChar);   // ####
			}
			in.close();

			// ...

			String[] lines = data.split("\n");
			String line;
			String key;
			String value;

			for (int i=0; i<lines.length ;i++) {

				line = lines[i];

				if (line != "") {   // ####lage den bedre slik at whitespace tåles?

					int pos = line.indexOf("=");
					if (pos >= 0) {
						key   = line.substring(0, pos);                 // ####lage den bedre slik at whitespace tåles?
						//System.out.println("key='" + key + "'");
						value = line.substring(pos+1, line.length());   // ####lage den bedre slik at whitespace tåles?
						//System.out.println("value='" + value + "'");
					} else {

						// illegal syntax

						ErrorMessage.error("Illegal syntax in settings file: " + line);
						return false;

					}

					if        (key.equals("relevantElementNames")) {

						// relevant elements - names of alignable elements

						if (target.equals("dialog")) {
							relevantElementNamesTextField.setText(value);
						} else {
							model.setRelevantElementNames(value);
						}

					} else if (key.equals("relevantAncestorElementNames")) {

						// relevant elements - names of ancestor elements of alignable elements

						if (target.equals("dialog")) {
							relevantAncestorElementNamesTextField.setText(value);
						} else {
							model.setRelevantAncestorElementNames(value);
						}

					} else if (key.equals("specialCharacters")) {

						// special characters

						if (target.equals("dialog")) {
							specialCharactersTextField.setText(value);
						} else {
							model.setSpecialCharacters(value);
						}

					} else if (key.equals("scoringCharacters")) {

						// score-giving characters

						if (target.equals("dialog")) {
							scoringCharactersTextField.setText(value);
						} else {
							model.setScoringCharacters(value);
						}

					} else if (key.equals("lengthRatio")) {

						// length ratio

						try {
							if (target.equals("dialog")) {
								lengthRatioSpinner.setValue(Float.parseFloat(value));
							} else {
								model.setLengthRatio(Float.parseFloat(value));
							}
						} catch (NumberFormatException e) {
							ErrorMessage.error("Number format error in decimal value in settings file:\n" + line);
							return false;
						}

					} else if (key.equals("diceMinWordLength")) {

						// dice settings - minimum word length

						try {
							if (target.equals("dialog")) {
								diceMinWordLengthSpinner.setValue(Integer.parseInt(value));
							} else {
								model.setDiceMinWordLength(Integer.parseInt(value));
							}
						} catch (NumberFormatException e) {
							ErrorMessage.error("Number format error in integer value in settings file:\n" + line);
							return false;
						}

					} else if (key.equals("diceMinCountingScore")) {

						// dice settings - raw score limit

						try {
							if (target.equals("dialog")) {
								diceMinCountingScoreSpinner.setValue(Float.parseFloat(value));
							} else {
								model.setDiceMinCountingScore(Float.parseFloat(value));
							}
						} catch (NumberFormatException e) {
							ErrorMessage.error("Number format error in decimal value in settings file:\n" + line);
							return false;
						}

					} else if (key.equals("largeClusterScorePercentage")) {

						// 'large cluster' settings

						try {
							if (target.equals("dialog")) {
								largeClusterScorePercentageSpinner.setValue(Integer.parseInt(value));
							} else {
								model.setLargeClusterScorePercentage(Integer.parseInt(value));
							}
						} catch (NumberFormatException e) {
							ErrorMessage.error("Number format error in integer value in settings file:\n" + line);
							return false;
						}

					} else if (key.equals("anchorWordMatchWeight")) {

						// weights - anchor words

						try {
							if (target.equals("dialog")) {
								anchorWordMatchWeightSpinner.setValue(Float.parseFloat(value));
							} else {
								model.setAnchorWordMatchWeight(Float.parseFloat(value));
							}
						} catch (NumberFormatException e) {
							ErrorMessage.error("Number format error in decimal value in settings file:\n" + line);
							return false;
						}

					} else if (key.equals("anchorPhraseMatchWeight")) {

						// weights - anchor phrases

						try {
							if (target.equals("dialog")) {
								anchorPhraseMatchWeightSpinner.setValue(Float.parseFloat(value));
							} else {
								model.setAnchorPhraseMatchWeight(Float.parseFloat(value));
							}
						} catch (NumberFormatException e) {
							ErrorMessage.error("Number format error in decimal value in settings file:\n" + line);
							return false;
						}

					} else if (key.equals("properNameMatchWeight")) {

						// weights - proper names

						try {
							if (target.equals("dialog")) {
								properNameMatchWeightSpinner.setValue(Float.parseFloat(value));
							} else {
								model.setProperNameMatchWeight(Float.parseFloat(value));
							}
						} catch (NumberFormatException e) {
							ErrorMessage.error("Number format error in decimal value in settings file:\n" + line);
							return false;
						}

					} else if (key.equals("diceMatchWeight")) {

						// weights - dice words

						try {
							if (target.equals("dialog")) {
								diceMatchWeightSpinner.setValue(Float.parseFloat(value));
							} else {
								model.setDiceMatchWeight(Float.parseFloat(value));
							}
						} catch (NumberFormatException e) {
							ErrorMessage.error("Number format error in decimal value in settings file:\n" + line);
							return false;
						}

					} else if (key.equals("dicePhraseMatchWeight")) {

						// weights - dice phrases

						try {
							if (target.equals("dialog")) {
								dicePhraseMatchWeightSpinner.setValue(Float.parseFloat(value));
							} else {
								model.setDicePhraseMatchWeight(Float.parseFloat(value));
							}
						} catch (NumberFormatException e) {
							ErrorMessage.error("Number format error in decimal value in settings file:\n" + line);
							return false;
						}

					} else if (key.equals("numberMatchWeight")) {

						// weights - numbers

						try {
							if (target.equals("dialog")) {
								numberMatchWeightSpinner.setValue(Float.parseFloat(value));
							} else {
								model.setNumberMatchWeight(Float.parseFloat(value));
							}
						} catch (NumberFormatException e) {
							ErrorMessage.error("Number format error in decimal value in settings file:\n" + line);
							return false;
						}

					} else if (key.equals("scoringCharacterMatchWeight")) {

						// weights - scoring characters

						try {
							if (target.equals("dialog")) {
								scoringCharacterMatchWeightSpinner.setValue(Float.parseFloat(value));
							} else {
								model.setScoringCharacterMatchWeight(Float.parseFloat(value));
							}
						} catch (NumberFormatException e) {
							ErrorMessage.error("Number format error in decimal value in settings file:\n" + line);
							return false;
						}

					} else if (key.equals("maxPathLength")) {

						// path length

						try {
							if (target.equals("dialog")) {
								maxPathLengthSpinner.setValue(Integer.parseInt(value));
							} else {
								model.setMaxPathLength(Integer.parseInt(value));
							}
						} catch (NumberFormatException e) {
							ErrorMessage.error("Number format error in integer value in settings file:\n" + line);
							return false;
						}

					} else if (key.equals("ancestorInfo")) {

						// newline format ancestor info - options

						try {
							if (target.equals("dialog")) {
								ancestorInfoRadioButtonPanel.setChoice(value);
							} else {
								if        (value.equals(AncestorInfoRadioButtonPanel.ANCESTORINFORADIOSTRINGS[AncestorInfoRadioButtonPanel.NONE] )) {
									model.setAncestorInfoChoice(AncestorInfoRadioButtonPanel.NONE);
								} else if (value.equals(AncestorInfoRadioButtonPanel.ANCESTORINFORADIOSTRINGS[AncestorInfoRadioButtonPanel.ALL]  )) {
									model.setAncestorInfoChoice(AncestorInfoRadioButtonPanel.ALL);
								} else if (value.equals(AncestorInfoRadioButtonPanel.ANCESTORINFORADIOSTRINGS[AncestorInfoRadioButtonPanel.DENY] )) {
									model.setAncestorInfoChoice(AncestorInfoRadioButtonPanel.DENY);
								} else if (value.equals(AncestorInfoRadioButtonPanel.ANCESTORINFORADIOSTRINGS[AncestorInfoRadioButtonPanel.ALLOW])) {
									model.setAncestorInfoChoice(AncestorInfoRadioButtonPanel.ALLOW);
								} else {
									ErrorMessage.error("Unknown value in settings file:\n" + line);
									return false;
								}
							}
						} catch (AncestorInfoRadioException e) {
							ErrorMessage.error("Unknown value in settings file:\n" + line);
							return false;
						}

					} else if (key.equals("ancestorInfoElementNames")) {

						// newline format ancestor info - element names

						if (target.equals("dialog")) {
							ancestorInfoElementNamesTextField.setText(value);
						} else {
							model.setAncestorInfoElementNames(value);
						}

					} else if (key.equals("ancestorInfoAttributeNames")) {

						// newline format ancestor info - attribute names

						if (target.equals("dialog")) {
							ancestorInfoAttributeNamesTextField.setText(value);
						} else {
							model.setAncestorInfoAttributeNames(value);
						}

					} else {

						// error. unknown key

						ErrorMessage.error("Unknown key in settings file:\n" + line);
						return false;

					}

				}

			}

			// ...........

			// ... file name ...
			model.setSettingsFilename(f.getName());
			// also show in gui
			gui.setSettingsFilenameLabel(f.getName());

            return true;

        } catch (Exception e) {

            ErrorMessage.error("Can't load settings file " + f.getName() + "\nException:\n" + e.toString());

            return false;

        }

	}

	private boolean saveFile(File f) {

		//System.out.println("saveFile() er under implementering");

		// ###se evt kommentarer i AnchorDialog
		OutputStream fOut;
		OutputStream bOut;
		Charset cs;
		OutputStreamWriter out;

        try {

			// ...

			// ###se evt kommentarer i AnchorDialog
			fOut = new FileOutputStream(f);
			bOut = new BufferedOutputStream(fOut);
			cs = Charset.forName("UTF-8");
			out = new OutputStreamWriter(bOut, cs);

        } catch (Exception e) {
		//} catch (IOException e) { kanskje heller bruke denne ############

            ErrorMessage.error("Can't open file " + f.getName() + "\nException:\n" + e.toString());

            return false;

        }

		// get setting values

		String data = "";

		// relevant elements

		data += "relevantElementNames="         + relevantElementNamesTextField.getText()         + "\n";
		data += "relevantAncestorElementNames=" + relevantAncestorElementNamesTextField.getText() + "\n";

		// special characters

		// ############# dangerous? must strip whitespace. must check for duplicates
		data += "specialCharacters=" + specialCharactersTextField.getText() + "\n";

		// score-giving characters

		data += "scoringCharacters=" + scoringCharactersTextField.getText() + "\n";

		// length ratio

		data += "lengthRatio=" + String.valueOf(((Float)lengthRatioSpinner.getValue()).floatValue()) + "\n";

		// dice settings

		data += "diceMinWordLength="    + ((Integer)diceMinWordLengthSpinner.getValue()).toString()                    + "\n";
		data += "diceMinCountingScore=" + String.valueOf(((Float)diceMinCountingScoreSpinner.getValue()).floatValue()) + "\n";

		// 'large cluster' settings

		data += "largeClusterScorePercentage=" + ((Integer)largeClusterScorePercentageSpinner.getValue()).toString() + "\n";

		// weights

		data += "anchorWordMatchWeight="       + String.valueOf(((Float)anchorWordMatchWeightSpinner.getValue()).floatValue())       + "\n";
		data += "anchorPhraseMatchWeight="     + String.valueOf(((Float)anchorPhraseMatchWeightSpinner.getValue()).floatValue())     + "\n";
		data += "properNameMatchWeight="       + String.valueOf(((Float)properNameMatchWeightSpinner.getValue()).floatValue())       + "\n";
		data += "diceMatchWeight="             + String.valueOf(((Float)diceMatchWeightSpinner.getValue()).floatValue())             + "\n";
		data += "dicePhraseMatchWeight="       + String.valueOf(((Float)dicePhraseMatchWeightSpinner.getValue()).floatValue())       + "\n";
		data += "numberMatchWeight="           + String.valueOf(((Float)numberMatchWeightSpinner.getValue()).floatValue())           + "\n";
		data += "scoringCharacterMatchWeight=" + String.valueOf(((Float)scoringCharacterMatchWeightSpinner.getValue()).floatValue()) + "\n";

		// path length

		data += "maxPathLength=" + ((Integer)maxPathLengthSpinner.getValue()).toString() + "\n";

		// newline format ancestor info

		int c;
		try {
			c = ancestorInfoRadioButtonPanel.getChoice();
		} catch (AncestorInfoRadioException e2) {
			// program error ###
			ErrorMessage.programError("Error in ancestor info radio button group");
			c = AncestorInfoRadioButtonPanel.NONE;
		}
		data += "ancestorInfo=" + AncestorInfoRadioButtonPanel.ANCESTORINFORADIOSTRINGS[c] + "\n";

		data += "ancestorInfoElementNames="   + ancestorInfoElementNamesTextField.getText()   + "\n";
		data += "ancestorInfoAttributeNames=" + ancestorInfoAttributeNamesTextField.getText() + "\n";

		//System.out.println("data=" + data);

        try {

			// write to file

			out.write(data, 0, data.length());
			out.close();

        } catch (Exception e) {
		//} catch (IOException e) { kanskje heller bruke denne ############

            ErrorMessage.error("Can't write to file " + f.getName() + "\nException:\n" + e.toString());

            return false;

        }

		// ... file name ...
		model.setSettingsFilename(f.getName());
		// also show in gui
		gui.setSettingsFilenameLabel(f.getName());

		return true;

	}
	// end 2006-09-20b

	// hvor skal denne? §§§nå er den både i AlignGui og Settings og her
	/** Returns an ImageIcon, or null if the path was invalid. */
	protected static ImageIcon createImageIcon(String path, String description) {
		java.net.URL imgURL = SettingsDialog.class.getResource(path);
		if (imgURL != null) {
			return new ImageIcon(imgURL, description);
		} else {
			//System.err.println("Couldn't find file: " + path);
			return null;
		}
	}

}