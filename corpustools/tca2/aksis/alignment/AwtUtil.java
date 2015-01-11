/*
 * AwtUtil.class
 *
 *              Copyright(c) 2001 Johan Utne Poppe,
 *         Senter for humanistisk informasjonsteknologi,
 *                    Universitetet i Bergen.
 *                      All rights reserved.
 */

package aksis.alignment;

import java.awt.*;

/**
 * A class to hold some general utility methods for
 * awt use.
 * @author Johan Utne Poppe
 */

public class AwtUtil {

    /** the component to work on. */
    private Container client;

    /** the layout to use */
    private GridBagLayout layout;

    /** the constraints for the layout */
    private GridBagConstraints constraints;

    /**
     * Creates a util object to store some data, to avoid giving some
     * parameters often.
     * @param layout A GridBagLayout.
     * @param rammer A GridBagConstraints
     */

    public AwtUtil(Container client,
                   GridBagLayout layout,
                   GridBagConstraints constraints) {
        this.client = client;
        this.layout = layout;
        this.constraints = constraints;
    }

    /**
     * Adds an element to the gridbaglayout given in the constructor
     * @param e The element to add
     */

    public void addInGridBag(Component element) {
        layout.setConstraints(element, constraints);
        client.add(element);
    } //add(element


    /**
     * Traverse the component hierarchy of c up to a Frame,
     * and return that frame
     * @param c a component
     * @return the toplevel container containing c
     */

    public static Frame getTopFrame(Component c) {
        while (!(c instanceof Frame) && c != null) {
            c = c.getParent();
        }
        return (Frame)c;
    }

}
