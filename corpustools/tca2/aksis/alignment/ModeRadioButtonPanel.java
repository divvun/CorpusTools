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

/**
 *
 * @author Oystein Reigem
 */

public class ModeRadioButtonPanel extends JPanel {

  public ButtonGroup rbg;

  //public ModeRadioButtonPanel() {
  public ModeRadioButtonPanel(Color bgColor, Font font) {

    // set the layout to a GridBagLayout
	GridBagLayout layout = new GridBagLayout();
	setLayout(layout);
	GridBagConstraints c = new GridBagConstraints();
	//c.insets = new Insets(3,3,3,3);
	c.anchor = GridBagConstraints.WEST;

    // declare a radio button
    JRadioButton radioButton;

    // instantiate a ButtonGroup for functional
    // association among radio buttons
    rbg = new ButtonGroup();

    // create a label for the group
    JLabel label = new JLabel("Mode: ");
    label.setFont(font);

	layout.setConstraints(label, c);
	add(label);

    // add first radio button to the pane
    //Color transparent = new Color(0f, 0f, 0f, 0f);   // 4th parameter = alpha = 0.0 = transparent
    radioButton = new JRadioButton("One at a time");
    //radioButton.setBackground(transparent);   // ### doesn't work. når musen føres over radioknappen, får den gjerne grønnfarge (som alle JButton i grensesnittet), og tekst kommer skrevet flere ganger
    radioButton.setOpaque(false);   // ### mye bedre!!!
    radioButton.setBackground(bgColor);
    radioButton.setFont(font);
	layout.setConstraints(radioButton, c);
	add(radioButton);

    // set key accelerator
    radioButton.setMnemonic(KeyEvent.VK_O);   // ################

    // add the button to the ButtonGroup
    rbg.add(radioButton);

    // set this radio button to be the default
    radioButton.setSelected(true);

    // set up second and third radio buttons
    radioButton = new JRadioButton("Skip 1-1");
    //radioButton.setBackground(transparent);
    radioButton.setOpaque(false);
    radioButton.setBackground(bgColor);
    radioButton.setFont(font);
    radioButton.setMnemonic(KeyEvent.VK_S);   // ################
	layout.setConstraints(radioButton, c);
	add(radioButton);
    rbg.add(radioButton);
    radioButton = new JRadioButton("Automatic");
    //radioButton.setBackground(transparent);
    radioButton.setOpaque(false);
    radioButton.setBackground(bgColor);
    radioButton.setFont(font);
    radioButton.setMnemonic(KeyEvent.VK_A);   // ################
	layout.setConstraints(radioButton, c);
	add(radioButton);
    rbg.add(radioButton);
  }
}

