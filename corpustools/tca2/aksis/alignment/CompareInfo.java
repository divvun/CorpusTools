/*
 * CompareInfo.java
 *
 * ...class for a component to show info about how elements compare
 * ...
 * ...
 */

package aksis.alignment;

import java.util.*;
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import java.awt.geom.*;

class CompareInfo extends JPanel {

	//AlignmentModel model;
	AlignGui gui;
	boolean on;

	/*
	public void paintComponent(Graphics g) {
		super.paintComponent(g);
		...
	}
	*/

	CompareInfo() {
		on = false;
	}

	public void paint(Graphics g) {
	//public void paintOffscreen(Graphics g) {   // ### fikk ikke denne til å funke. slo aldri til. kanskje den bare gjelder for vinduer???

		//System.out.println("paint");
		//System.out.println("paintOffscreen");
		super.paint(g);
		//super.paintOffscreen(g);   ### finnes ikke

		Graphics2D g2 = (Graphics2D)g;

		if (on) {

			//System.out.println("paint(). gui.model.compare.matrix = " + gui.model.compare.matrix);

			// visualize path scores for all 1-1, 1-2 and 2-1 pairings

			//g2.setColor(Color.black);

			g2.setFont(new Font("Courier New", Font.PLAIN, 10));

			int first;
			Iterator it = gui.model.compare.matrix.cells.keySet().iterator();
			while (it.hasNext()) {

				String key = (String)it.next();
				//System.out.println("key = " + key);
				String[] temp = key.split(",");
				first = gui.model.compare.elementsInfo[0].getFirst();
				int iy = Integer.parseInt(temp[0]) - first;
				int iy2 = Integer.parseInt(temp[2]) - first;
				first = gui.model.compare.elementsInfo[1].getFirst();
				int ix = Integer.parseInt(temp[1]) - first;
				int ix2 = Integer.parseInt(temp[3]) - first;

				////float score = ((CompareCells)(gui.model.compare.matrix.cells.get(key))).bestPathScore.getScore();
				////float score = ((CompareCells)(gui.model.compare.matrix.cells.get(key))).score;
				float score = ((CompareCells)(gui.model.compare.matrix.cells.get(key))).getScore();
				//if (iy == 0 && iy2 == iy && ix == 0 && ix2 == ix) {
				if (iy == 0 && ix == 0) {
					//¤//System.out.println("show(). iy=" + iy + "-" + iy2 + ". ix=" + ix + "-" + ix2 + ". score=" + score);
				}
				// ### not always correct to divide by max path length, e.g, at towards the end of the texts, where paths are shorter.
				// ### different alternative: spread range of current intensities over the whole range 0.-1.
				// ### uh - totally wrong to divide by path length, because we show cell score, not path score
				//float intensity = score / (5.f * gui.model.getMaxPathLength());
				float intensity = score / 20.f;
				//if (intensity < 0.f) { intensity = 0.f; }   // #### skal aldri forekomme
				Color c;
				if (intensity < 0.f) {
					c = Color.gray;   // 1-2 or 2-1 that is killed
				} else if (intensity > 1.f) {
					//System.out.println("1");
					c = Color.yellow;   // beyond the scale
					//System.out.println("1");
				} else {
					//System.out.println("2");
					c = new Color(1.f, 1.f - intensity, 1.f - intensity);   // various intensities of red
					//System.out.println("2");
				}
				g2.setColor(c);

				//
				int ly = iy2 - iy + 1;
				int lx = ix2 - ix + 1;
				int x, y;

				if (ly == 1) {
					if (lx == 1) {
						// 1-1
						x = 10 + ix*19;
						y = 10 + iy*19;
						g2.fillRect(x, y, 6, 6);
						//// 1-1 score
						//g2.setColor(Color.black);
						//g2.drawString("" + Math.round(score), x, y+6);   // ¤¤¤ long values will get partly overwritten by 1-2 rectangles
						//g2.setColor(c);
					} else if (lx == 2) {
						// 1-2
						x = 10 + ix*19 + 8;
						y = 10 + iy*19 + 1;
						g2.fillRect(x, y, 9, 4);
					}
				} else if (ly == 2) {
					if (lx == 1) {
						// 2-1
						x = 10 + ix*19 + 1;
						y = 10 + iy*19 + 8;
						g2.fillRect(x, y, 4, 9);
					}
				}

			}

			// do text (numbers) afterwards, so it doesn't get overwritten

			g2.setColor(Color.black);

			it = gui.model.compare.matrix.cells.keySet().iterator();
			while (it.hasNext()) {

				String key = (String)it.next();
				String[] temp = key.split(",");
				first = gui.model.compare.elementsInfo[0].getFirst();
				int iy = Integer.parseInt(temp[0]) - first;
				int iy2 = Integer.parseInt(temp[2]) - first;
				first = gui.model.compare.elementsInfo[1].getFirst();
				int ix = Integer.parseInt(temp[1]) - first;
				int ix2 = Integer.parseInt(temp[3]) - first;

				////float score = ((CompareCells)(gui.model.compare.matrix.cells.get(key))).bestPathScore.getScore();
				////float score = ((CompareCells)(gui.model.compare.matrix.cells.get(key))).score;
				float score = ((CompareCells)(gui.model.compare.matrix.cells.get(key))).getScore();
				//if (iy == 0 && iy2 == iy && ix == 0 && ix2 == ix) {
				if (iy == 0 && ix == 0) {
					//¤//System.out.println("show(). iy=" + iy + "-" + iy2 + ". ix=" + ix + "-" + ix2 + ". score=" + score);
				}

				//
				int ly = iy2 - iy + 1;
				int lx = ix2 - ix + 1;
				int x, y;

				if (ly == 1) {
					if (lx == 1) {
						// 1-1
						x = 10 + ix*19;
						y = 10 + iy*19;
						// 1-1 score
						g2.drawString("" + Math.round(score), x, y+6);
					}
				}

			}

		} else {

			g2.clearRect(0, 0, 1000, 1000);   // ###########

		}
	}

	// tell the object where to find the data to visualize
	//public void setModel(AlignmentModel model) {
	public void setGui(AlignGui gui) {
		//this.model = model;
		this.gui = gui;
	}

	// turn visualizing on or off.
	// these methods do not paint by themselves. §§§§ burde vel det
	public void on() {
		this.on = true;
	}
	public void off() {
		this.on = false;
	}

}

