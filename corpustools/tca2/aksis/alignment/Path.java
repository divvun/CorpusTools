package aksis.alignment;

import java.util.Iterator;
import java.util.List;
import java.util.ArrayList;

class Path implements Cloneable {

	// a list of PathStep objects...
	List<PathStep> steps = new ArrayList<PathStep>();
	// ...leading to this position
	// ############# 2005-11-02.
	// the position is meant to be absolute, i.e, the actual position in the texts.
	// but there seems to be some confusion. one or more places in the app treats position as relative.
	// tries to fix that now.
	// ############### false alarm!? but i though i saw relative values from println
	int[] position = new int[Alignment.NUM_FILES];
	// but path object contains no explicit info about which position the path starts

	// ### only meant to be used when we need a copy of a path.
	// clunky way to get a copy?
	public Path() {
		//System.out.println("Path() constructor");
	}

	public Path(int[] initialPosition) {
		//¤//System.out.println("Path(int[] initialPosition) constructor. initialPosition=" + initialPosition[0] + "," + initialPosition[1]);
		position = initialPosition;
	}

	public boolean equals(Path path) {
		// ####### dodgy?
		return (this.toString().equals(path.toString()));
	}

	public void extend(PathStep step) {
		//steps.add(step);
		//System.out.println("før steps.add(). steps.size() = " + steps.size());
		//System.out.println("skal adde steg " + step);
		steps.add((PathStep)step.clone());   // §§§ dette må vel være riktigere
		//System.out.println("etter steps.add(). steps.size() = " + steps.size());
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			position[t] += step.increment[t];
		}
	}

	public String toString() {
		String temp = "[";
		Iterator<PathStep> it = steps.iterator();
		boolean first = true;
		while (it.hasNext()) {
			if (!first) { temp += ", "; }
			PathStep step = (PathStep)it.next();
			temp += "{";
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				if (t > 0) { temp += ","; }
				temp += Integer.toString(step.increment[t]);
			}
			temp += "}";
			first = false;
		}
		temp += "]->";
		temp += "{";
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			if (t > 0) { temp += ","; }
			temp += position[t];
		}
		temp += "}";
		return temp;
	}

	// ¤¤¤ brukes visst ikke av clone()
	public List<PathStep> getSteps(){
		return steps;
	}

	// brukes av clone()
	public void setSteps(List<PathStep> steps){
		this.steps = steps;
	}

    public Object clone() {

        try {
			// first make exact bitwise copy
			Path copy = (Path)super.clone();
			// a new arraylist of PathStep objects is created
			copy.steps = new ArrayList<PathStep>();
			// then copies of the original's PathStep objects are added
			Iterator<PathStep> it = steps.iterator();
			while (it.hasNext()) {
				PathStep stepCopy = (PathStep)((PathStep)it.next()).clone();   // PathStep has its own deep copy
				copy.steps.add(stepCopy);
			}
			// a new array of int is created
			copy.position = new int[Alignment.NUM_FILES];
			// then the int values are set
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				copy.position[t] = position[t];
			}
			return copy;
        } catch (CloneNotSupportedException e) {
            throw new Error("This should not occur since we implement Cloneable");
        }

	}

    public int getLengthInSentences() {
		// the number of sentences in the path, counting in both texts
		int count = 0;
		Iterator<PathStep> it = steps.iterator();
		while (it.hasNext()) {
			PathStep step = (PathStep)it.next();
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				count += step.increment[t];
			}
		}
		//System.out.println(">>> getLengthInSentences teller " + count + " setninger");
		return count;
	}

}

