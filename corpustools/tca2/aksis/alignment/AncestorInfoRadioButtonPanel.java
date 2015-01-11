package aksis.alignment;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;

class AncestorInfoRadioButtonPanel extends JPanel {

	// radio buttons "index" value
	public static int NONE = 0;
	public static int ALL = 1;
	public static int DENY = 2;
	public static int ALLOW = 3;
	// 2006-09-21
	// friendly text version
	public static String[] ANCESTORINFORADIOSTRINGS = { "none", "all", "deny", "allow" };
	// each button
	public JRadioButton[] radioButtons = new JRadioButton[4];
	//// each button, or rather each button's "ButtonModel"
	//public ButtonModel[] buttonModel;
	// end 2006-09-21

	public ButtonGroup rbg;

	public AncestorInfoRadioButtonPanel(int mode, Color bgColor) {

		// set the layout to a GridBagLayout
		GridBagLayout layout = new GridBagLayout();
		setLayout(layout);
		GridBagConstraints c = new GridBagConstraints();
		c.anchor = GridBagConstraints.NORTH;

		c.gridy = 0;

		// declare a radio button
		JRadioButton radioButton;

		// instantiate a ButtonGroup for functional
		// association among radio buttons
		rbg = new ButtonGroup();

		// create a label for the group
		JLabel label = new JLabel("Ancestor element info to be included in newline format output:");

		c.gridy++;
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;
		layout.setConstraints(label, c);
		add(label);

		// add first radio button to the pane
		radioButton = new JRadioButton("None");
		radioButton.setBackground(bgColor);
		c.gridy++;
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;
		layout.setConstraints(radioButton, c);
		add(radioButton);

		// set key accelerator
		radioButton.setMnemonic(KeyEvent.VK_N);   // ################

		// add the button to the ButtonGroup
		rbg.add(radioButton);

		// ..
		//buttonModel[NONE] = radioButton.getModel();   // 2006-09-21
		radioButtons[NONE] = radioButton;   // 2006-09-21

		// set this radio button to be the default?
		if (mode == NONE) {
			radioButton.setSelected(true);
		}

		// set up second, third and fourth radio buttons

		radioButton = new JRadioButton("All");
		radioButton.setBackground(bgColor);
		radioButton.setMnemonic(KeyEvent.VK_A);   // ################
		c.gridy++;
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;
		layout.setConstraints(radioButton, c);
		add(radioButton);
		rbg.add(radioButton);
		if (mode == ALL) {
			radioButton.setSelected(true);
		}
		//buttonModel[ALL] = radioButton.getModel();   // 2006-09-21
		radioButtons[ALL] = radioButton;   // 2006-09-21

		radioButton = new JRadioButton("Deny elements and attributes listed below");
		radioButton.setBackground(bgColor);
		radioButton.setMnemonic(KeyEvent.VK_D);   // ################
		c.gridy++;
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;
		layout.setConstraints(radioButton, c);
		add(radioButton);
		rbg.add(radioButton);
		if (mode == DENY) {
			radioButton.setSelected(true);
		}
		//buttonModel[DENY] = radioButton.getModel();   // 2006-09-21
		radioButtons[DENY] = radioButton;   // 2006-09-21

		radioButton = new JRadioButton("Only allow elements and attributes listed below");
		radioButton.setBackground(bgColor);
		radioButton.setMnemonic(KeyEvent.VK_O);   // ################
		c.gridy++;
		c.weighty = 1;
		c.gridx = 0;
		c.gridwidth = 1;
		c.weightx = 0;
		c.fill = GridBagConstraints.HORIZONTAL;
		layout.setConstraints(radioButton, c);
		add(radioButton);
		rbg.add(radioButton);
		if (mode == ALLOW) {
			radioButton.setSelected(true);
		}
		//buttonModel[ALLOW] = radioButton.getModel();   // 2006-09-21
		radioButtons[ALLOW] = radioButton;   // 2006-09-21

	}

	//public int getChoice() {
	public int getChoice() throws AncestorInfoRadioException {   // 2006-09-21
		// (getSelection returns not the selected button itself but a ButtonModel) // 2006-09-21
		int mnemonic = rbg.getSelection().getMnemonic();
		if        (mnemonic == KeyEvent.VK_N) {   // ################
			return NONE;
		} else if (mnemonic == KeyEvent.VK_A) {   // ################
			return ALL;
		} else if (mnemonic == KeyEvent.VK_D) {   // ################
			return DENY;
		} else if (mnemonic == KeyEvent.VK_O) {   // ################
			return ALLOW;
		} else {
			// ##### program error ####
			//return NONE;
			throw new AncestorInfoRadioException();
		}
		/*
		// 2006-09-21
		ButtonModel bM = rbg.getSelection();
		if        (bM == buttonModel[NONE] ) {
			return NONE;
		// end 2006-09-21
		} else if (bM == buttonModel[ALL]  ) {
			return ALL;
		} else if (bM == buttonModel[DENY] ) {
			return DENY;
		} else if (bM == buttonModel[ALLOW]) {
			return ALLOW;
		} else {
			// ##### program error ####
			throw new AncestorInfoRadioException();
		}
		// end 2006-09-21
		*/
	}

	// 2006-09-21

	public void setChoice(String value) throws AncestorInfoRadioException {
		if        (value.equals(ANCESTORINFORADIOSTRINGS[NONE] )) {
			radioButtons[NONE].setSelected(true);
		} else if (value.equals(ANCESTORINFORADIOSTRINGS[ALL]  )) {
			radioButtons[ALL].setSelected(true);
		} else if (value.equals(ANCESTORINFORADIOSTRINGS[DENY] )) {
			radioButtons[DENY].setSelected(true);
		} else if (value.equals(ANCESTORINFORADIOSTRINGS[ALLOW])) {
			radioButtons[ALLOW].setSelected(true);
		} else {
			throw new AncestorInfoRadioException();
		}
	}
	// end 2006-09-21

}

