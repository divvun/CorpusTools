package aksis.alignment;

class PathStep implements Cloneable {

	int[] increment = new int[Alignment.NUM_FILES];

	public PathStep() {
	}

	public PathStep(int[] inc) {
		increment = inc;
	}

	public boolean is11() {
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			if (increment[t] != 1) {
				return false;
			}
		}
		return true;
	}

	public String toString() {
		String temp = "{";
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			if (t>0) { temp += ","; }
			temp += Integer.toString(increment[t]);
		}
		temp += "}";
		return temp;
	}

    public Object clone() {

        try {
			// first make exact bitwise copy
			PathStep copy = (PathStep)super.clone();
			// a new array of int is created
			copy.increment = new int[Alignment.NUM_FILES];
			// then copy over the int values
			for (int t=0; t<Alignment.NUM_FILES; t++) {
				copy.increment[t] = increment[t];
			}
			return copy;
        } catch (CloneNotSupportedException e) {
            throw new Error("This should not occur since we implement Cloneable");
        }

	}

}

