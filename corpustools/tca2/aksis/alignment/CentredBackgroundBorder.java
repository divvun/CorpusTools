/*
 * CentredBackgroundBorder.java
 *
 * ...
 * ...
 * ...
 */

package aksis.alignment;

import java.awt.*;
import java.awt.geom.*;
import java.awt.image.*;
import java.io.*;
import javax.imageio.*;
import javax.swing.*;
import javax.swing.border.*;

// <http://forum.java.sun.com/thread.jspa?forumID=57&threadID=545064&start=3>
//
// Re: jbuttons over a image
// Author: DrLaszloJamf   Aug 9, 2004 10:32 AM (reply 3 of 7)
//
// I don't think subclassing JFrame is a good approach here - in any case its the job of the content pane or
// something in it to render this background image.
//
// My favorite way to add a background image to a container is to let the border do it: no need to subclass!

public class CentredBackgroundBorder implements Border {

    private final BufferedImage image;

    public CentredBackgroundBorder(BufferedImage image) {
        this.image = image;
    }

    public void paintBorder(Component c, Graphics g, int x, int y, int width, int height) {
        int x0 = x + (width-image.getWidth())/2;
        int y0 = y + (height-image.getHeight())/2;
        AffineTransform tx = AffineTransform.getTranslateInstance(x0, y0);
        ((Graphics2D)g).drawRenderedImage(image, tx);
    }

    public Insets getBorderInsets(Component c) {
        return new Insets(0,0,0,0);
    }

    public boolean isBorderOpaque() {
        return true;
    }

}

