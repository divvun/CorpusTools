/*
 * RefComparator.java
 *
 * ...
 * ...
 * ...
 */

package aksis.alignment;

// compares two references (Ref) in clusters (Cluster),
//// first on text number, then on word value
// first on math type (e.g, number of anchor word entry), then on text number, then on word value
public class RefComparator implements java.util.Comparator {

    public int compare(Object o1,Object o2) throws ClassCastException {

        if (!(o1 instanceof Ref)) {
            throw new ClassCastException();
        }
        if(!(o2 instanceof Ref)) {
            throw new ClassCastException();
        }

        // 2006-04-05

        int matchType1 = ((Ref)o1).getMatchType();
        int matchType2 = ((Ref)o2).getMatchType();

        if (matchType1 < matchType2) {

            return -1;

        } else if (matchType1 > matchType2) {

            return 1;

        } else {

        // end 2006-04-05

			int t  = ((Ref)o1).getT();   // 2006-04-05
			int tt = ((Ref)o2).getT();   // 2006-04-05

			if (t < tt) {

				return -1;

			} else if (t > tt) {

				return 1;

			} else {

				String word1 = ((Ref)o1).getWord();   // 2006-04-05
				String word2 = ((Ref)o2).getWord();   // 2006-04-05

				return word1.compareTo(word2);

			}

		}

    }

}

