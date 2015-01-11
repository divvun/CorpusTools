package aksis.alignment;

import java.util.Observable;

/**
 * separate thread for loading files.
 * to be more precise it's not for the process of reading a file into a DOM tree
 * but the processing of the elements we do afterwards.
 * but anyway it's a process we want to show progress for in gui components,
 * so we need to have it in a separate thread.
 */
class LoadFileRunnable extends Observable implements Runnable {

	AlignmentModel model;
	int t;
	int elementNumber;


	// (we need a constructor with some arguments
	// to get references to the stuff the thread is working with) ¤¤¤

	public LoadFileRunnable(AlignmentModel model, int t) {
		this.model = model;
		this.t = t;
	}

	// do ¤¤¤

	public void run() {

		int numElements = model.nodes[t].getLength();

		for (elementNumber = 0; elementNumber < numElements; elementNumber++) {

			AElement element = new AElement(model.nodes[t].item(elementNumber), elementNumber);
			model.unaligned.add(t, element);
			setChanged();
			notifyObservers(elementNumber+1);
		}
	}
}
