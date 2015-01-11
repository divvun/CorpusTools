/*
 * AnchorWordHitComparator.java
 *
 * ...
 * ...
 * ...
 */

package aksis.alignment;

public class AnchorWordHitComparator implements java.util.Comparator {

    public int compare(Object o1,Object o2) throws ClassCastException {

        if (!(o1 instanceof AnchorWordHit)) {
            throw new ClassCastException();
        }
        if(!(o2 instanceof AnchorWordHit)) {
            throw new ClassCastException();
        }

        int index1 = ((AnchorWordHit)o1).getIndex().intValue();
        int index2 = ((AnchorWordHit)o2).getIndex().intValue();

        if (index1 < index2) {

            return -1;

        } else if (index1 > index2) {

            return 1;

        } else {

			String word1 = ((AnchorWordHit)o1).getWord();
			String word2 = ((AnchorWordHit)o2).getWord();

			/*
			if (word1 < word2) {
				return -1;
			} else if (word1 > word2) {
				return 1;
			} else {
            	return 0;
			}
			*/
			return word1.compareTo(word2);

        }

    }

}

