/*
 * ShowCompare.java
 *
 * ...
 * ... BRUKES IKKE
 * ...
 */

package aksis.alignment;

import java.util.*;
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import java.awt.geom.*;

public class ShowCompare {

	//public ShowCompare() {
	//
	//}

	public static void show(AlignGui gui) {

		// ...

		Graphics g = gui.compareInfoGraphics;

		//System.out.println("show(). gui.model.compare.matrix = " + gui.model.compare.matrix);

		// visualize path scores for all 1-1, 1-2 and 2-1 pairings

		//g.setColor(Color.black);

		g.setFont(new Font("Courier New",Font.PLAIN, 10));

		int first;
		Iterator it = gui.model.compare.matrix.cells.keySet().iterator();
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
			// ### not always correct to divide by max path length, e.g, at towards the end of the texts, where paths are shorter.
			// ### different alternative: spread range of current intensities over the whole range 0.-1.
			float intensity = score / (5.f * gui.model.getMaxPathLength());
			Color c;
			if (intensity > 1.f) {
				c = new Color(1.f, 1.f, 0.f);
			} else {
				c = new Color(1.f, 1.f - intensity, 1.f - intensity);
			}
			g.setColor(c);

			//
			int ly = iy2 - iy + 1;
			int lx = ix2 - ix + 1;
			int x, y;

			if (ly == 1) {
				if (lx == 1) {
					// 1-1
					x = 10 + ix*19;
					y = 10 + iy*19;
					g.fillRect(x, y, 6, 6);
					// 1-1 score
					g.setColor(Color.black);
					g.drawString("" + Math.round(score), x, y+6);   // ¤¤¤ long values will get partly overwritten by 1-2 rectangles
					g.setColor(c);
				} else if (lx == 2) {
					// 1-2
					x = 10 + ix*19 + 8;
					y = 10 + iy*19 + 1;
					g.fillRect(x, y, 9, 4);
				}
			} else if (ly == 2) {
				if (lx == 1) {
					// 2-1
					x = 10 + ix*19 + 1;
					y = 10 + iy*19 + 8;
					g.fillRect(x, y, 4, 9);
				}
			}

		}

		/*
		int x, y;

		g.setColor(Color.cyan);
		for (int i=0; i<10; i++) {
			for (int j=0; j<10; j++) {
				x = 50 + i*19;
				y = 50 + j*19;
				g.fillRect(x, y, 6, 6);
			}
		}

		for (int i=0; i<10; i++) {
			for (int j=0; j<10; j++) {
				g.setColor(Color.red);
				x = 50 + i*19 + 8;
				y = 50 + j*19 + 1;
				g.fillRect(x, y, 9, 4);
				g.setColor(Color.yellow);
				x = 50 + i*19 + 1;
				y = 50 + j*19 + 8;
				g.fillRect(x, y, 4, 9);
			}
		}

		g.setColor(Color.black);
		for (int i=0; i<10; i++) {
			for (int j=0; j<10; j++) {
				x = 50 + i*19 - 7;
				y = 50 + j*19 - 7;
				g.drawRect(x, y, 19, 19);
			}
		}
		*/

	}

	public static void clear(AlignGui gui) {

		// ...

		Graphics g = gui.compareInfoGraphics;

		g.clearRect(0, 0, 500, 500);

	}

}




