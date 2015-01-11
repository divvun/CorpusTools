/*
 * AlignStatusLine.java
 *
 * ...
 * ...
 * ...
 */

package aksis.alignment;

import java.awt.*;
import javax.swing.*;
import java.util.Observer;
import java.util.Observable;

class AlignStatusText implements Observer {
	public void update(Observable obj, Object arg) {
		System.out.println("AlignStatusText changed: " + arg);
	}
}

class AlignStatusLine extends JPanel {

	public final static int PROGRESS_MIN = 0;
	public final static int PROGRESS_MAX = 100;
	public final static int MEMORY_USAGE_MIN = 0;
	public final static int MEMORY_USAGE_MAX = 100;

	private JTextField text;
	private JTextField counter;
	private JProgressBar progress;
	private JTextField memoryUsage;

	public AlignStatusLine() {

		super(new BorderLayout());

		//text = new JTextField(10);
		text = new JTextField(20);
		counter = new JTextField(10);   // ### not used

		UIManager.put("ProgressBar.selectionBackground", Color.black);
		UIManager.put("ProgressBar.selectionForeground", Color.white);
		UIManager.put("ProgressBar.foreground", Color.blue);
		UIManager.put("ProgressBar.cellLength", new Integer(5));
		UIManager.put("ProgressBar.cellSpacing", new Integer(1));
		progress = new JProgressBar();

		progress.setMinimum(PROGRESS_MIN);
		progress.setMaximum(PROGRESS_MAX);
		progress.setStringPainted(true);

		memoryUsage = new JTextField(5);

		Box b = new Box(BoxLayout.X_AXIS);
		b.add(progress);
		b.add(new JLabel("  Memory usage: "));
		b.add(memoryUsage);

		add(BorderLayout.WEST, text);
		add(BorderLayout.CENTER, counter);
		add(BorderLayout.EAST, b);

		clear();

	}

	void setText(String s) {
		text.setText(s);
		Rectangle rect = text.getBounds();
		rect.x = 0;
		rect.y = 0;
		text.paintImmediately(rect);
	}

	void clearText() {
		setText("");
	}

	void setCounter(int c) {
		counter.setText(Integer.toString(c));
		Rectangle rect = counter.getBounds();
		rect.x = 0;
		rect.y = 0;
		counter.paintImmediately(rect);
	}

	void clearCounter() {
		counter.setText("");
		Rectangle rect = counter.getBounds();
		rect.x = 0;
		rect.y = 0;
		counter.paintImmediately(rect);
		}

	void setProgress(int p) {
		progress.setVisible(true);
		progress.setValue(p);
		Rectangle rect = progress.getBounds();
		rect.x = 0;
		rect.y = 0;
		progress.paintImmediately(rect);
	}

	void clearProgress() {
		progress.setVisible(false);
		Rectangle rect = progress.getBounds();
		rect.x = 0;
		rect.y = 0;
		progress.paintImmediately(rect);
	}

	
	void setMemoryUsage(Integer memUsage) {
		memoryUsage.setText(memUsage.toString());
		Rectangle rect = memoryUsage.getBounds();
		rect.x = 0;
		rect.y = 0;
		memoryUsage.paintImmediately( rect );
	}

	void clearMemoryUsage() {
		memoryUsage.setText("");
		Rectangle rect = memoryUsage.getBounds();
		rect.x = 0;
		rect.y = 0;
		memoryUsage.paintImmediately( rect );
	}

	void clear() {
		clearText();
		clearCounter();
		clearProgress();
		setMemoryUsage(0);
	}
}


