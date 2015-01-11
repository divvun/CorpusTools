/*
 * QueueList.java
 *
 * ...
 * ...
 * @author Oystein Reigem
 */

package aksis.alignment;

import java.util.List;
import java.util.ArrayList;
import java.util.Iterator;
/*
 * list of QueueEntry objects
 */
class QueueList {

	List entry = new ArrayList();   // ### heller hete entries?

	// ### only used when making copy. clunky?
	QueueList() {
		//System.out.println("QueueList() constructor");
	}

	QueueList(AlignmentModel model, int[] position) {
		//¤//System.out.println("QueueList(model, position) constructor. position=" + position[0] + "," + position[1]);
		entry.add(new QueueEntry(position, 0));
	}

	public boolean empty() {
		return (entry.size() == 0);
	}

	public void add(QueueEntry queueEntry) {
		entry.add(queueEntry);
	}

	public boolean contains(QueueEntry queueEntry) {
		// checks to see if there already is an entry with the same path
		Iterator it = entry.iterator();
		while (it.hasNext()) {
			QueueEntry nextQueueEntry = (QueueEntry)it.next();
			if (nextQueueEntry.path.equals(queueEntry.path)) {
				return true;
			}
		}
		return false;
	}

	public void remove(int[] pos) {
		// remove any paths leading to position pos
		// (there should be at most 1 such path,
		// but this method will work even if there are more than one).
		// ###(the queue list contains paths of the same length, i think.
		// sometimes this method will be called to remove a path of a different length,
		// and that path is not in the list. no problem).
		// note! doesn't remove for real.
		// just marks the relevant entry (entries) as removed.
		// done this way so it's possible to loop through the list with an iterator
		//
		// #### 2005-11-02
		// OOOOOOPS!!!!!!!!
		// must also remove paths PASSING THROUGH position pos.
		// example:
		// we're at the very beginning of the texts.
		// correct aligment is all 1-1's.
		// the program has considered all paths of length 2.
		// it has found 1-2 + 2-1 to be the best path leading to position {2,2}.
		// in the process of extending paths of length 2 to paths of length 3,
		// the program arrives at 1-1 + 1-1 + 1-1, which also leads to position {2,2}.
		// this latter path has a better score,
		// so 1-2 + 2-1 must be removed (marked for removal).
		// where is it we remove inferior paths from?
		// we remove them from the list of paths of length 3, which is under construction.
		// but is there any 1-2 + 2-1 in that list?
		// no, not as such.
		// but there might be paths 1-2 + 2-1 + x-y, that PASS THROUGH position {2,2}.
		// ALL THOSE PATHS MUST BE REMOVED.
		//
		// or perhaps the program hasn't tried to extend 1-2 + 2-1 yet.
		// IN THAT CASE IT MUST BE KEPT FROM DOING SO.
		// in the general case it must also be kept from extending
		// any path that PASSES THROUGH the current position.
		//
		//¤//System.out.println("QueueList sin remove()");
		//List toRemove = new ArrayList();
		//System.out.println("class QueueList sin remove() skal fjerne alle entries med path som leder til, eller passerer gjennom, pos {" + pos[0] + "," + pos[1] + "}");
		boolean debug = false;
		//if ((pos[0] == 4) && (pos[1] == 4)) { System.out.println(">>> pos er 4,4"); debug = true; }
		//if ((pos[0] == 2) && (pos[1] == 3)) { System.out.println(">>> pos er 2,3"); debug = true; }
		//if (debug) { System.out.println(">>>>>>>>>>>>>>>>>>>>>>> START remove()"); }
		int t;
		Iterator it = entry.iterator();
		while (it.hasNext()) {
			QueueEntry queueEntry = (QueueEntry)it.next();
			//if ((pos[0] == 4) && (pos[1] == 4)) {
			//	System.out.println(">>> pos er 4,4. queueEntry = " + queueEntry + "\n");
			//}
			//if (debug) { System.out.println(">>> queueEntry = " + queueEntry + "\n"); }
			//boolean eq = true;
			boolean hit = false;   // if the path ends at or passes through the position
			// search backwards through path for position
			int[] current = new int[Alignment.NUM_FILES];
			// start at the path's end position
			//current = queueEntry.path.position;
			System.arraycopy(queueEntry.path.position, 0, current, 0, queueEntry.path.position.length);
			int currentIx = queueEntry.path.steps.size() - 1;   // index for the current place in the path. start at end
			//if (debug) { System.out.println(">>> currentIx = " + currentIx); }
			boolean done = false;
			while (!done) {
				// still hope of finding the position in the path?
				//if (debug) { System.out.println(">>> still hope of finding the position in the path?"); }
				boolean hope = true;
				for (t=0; t<Alignment.NUM_FILES; t++) {
					if (current[t] < pos[t]) {
						// no. the current position in the path is situated to the left of, or above,
						// the position we search for. there is no point in following the path further back
						//if (debug) { System.out.println(">>> no. the current position in the path is situated to the left of, or above, the position we search for. there is no point in following the path further back"); }
						hope = false;
						break;
					}
				}
				if (hope) {
					// yes. compare the current position in the path with the position we're looking for
					//if (debug) { System.out.println(">>> yes. compare the current position in the path with the position we're looking for"); }
					boolean eq = true;
					for (t=0; t<Alignment.NUM_FILES; t++) {
						if (current[t] != pos[t]) {
							eq = false;
							break;
						}
					}
					if (eq) {
						// hit. the current position in the path is the one we're looking for
						//if (debug) { System.out.println(">>> hit. the current position in the path is the one we're looking for"); }
						hit = true;
						done = true;
					} else {
						// miss. move back one step in the path
						//if (debug) { System.out.println(">>> miss. move back one step in the path"); }
						if (currentIx >= 0) {
							for (t=0; t<Alignment.NUM_FILES; t++) {
								current[t] -= ((PathStep)(queueEntry.path.steps.get(currentIx))).increment[t];
							}
							currentIx--;
						} else {
							// not possible. path exhausted
							//if (debug) { System.out.println(">>> not possible. path exhausted"); }
							done = true;
						}
					}
				} else {
					// no
					//if (debug) { System.out.println(">>> no"); }
					done = true;
				}
			}

			//for (int t=0; t<Alignment.NUM_FILES; t++) {
			//	if (pos[t] != queueEntry.path.position[t]) {
			//		//eq = false;
			//		hit = false;
			//		break;
			//	}
			//}
			//if (eq) {
			if (hit) {
				//toRemove.add(queueEntry);
				//System.out.println("\nclass QueueList sin remove() merker entry " + queueEntry + " for fjerning\n");
				queueEntry.remove();   // i.e, mark it for removal. will be removed for real by the calling method, using method below
				//System.out.println("class QueueList sin remove() skal fjerne entry " + queueEntry);
				if (debug) { System.out.println(">>> hit. mark for removal entry " + queueEntry + "\n"); }
				//it.remove();
			}
		}
		//it = toRemove.iterator();
		//System.out.println("class QueueList skal fjerne " + it.size() + " entries");
		//while (it.hasNext()) {
		//	QueueEntry queueEntry = (QueueEntry)it.next();
		//	//¤//System.out.println("QueueList sin remove() fjerner en entry");
		//	System.out.println("class QueueList sin remove() skal fjerne entry " + queueEntry);
		//	entry.remove(queueEntry);
		//}

		if (debug) { System.out.println(">>>>>>>>>>>>>>>>>>>>>>> END remove()"); }
	}

	public void removeForReal() {
		// remove for real all entries marked as removed
		Iterator it = entry.iterator();
		List toRemove = new ArrayList();
		while (it.hasNext()) {
			QueueEntry queueEntry = (QueueEntry)it.next();
			if (queueEntry.removed) {
				toRemove.add(queueEntry);
			}
		}
		it = toRemove.iterator();
		while (it.hasNext()) {
			QueueEntry queueEntry = (QueueEntry)it.next();
			//System.out.println("QueueList sin removeForReal() fjerner entry " + queueEntry);
			entry.remove(queueEntry);
		}

	}

	public String toString() {
		String temp = "[\n";
		Iterator it = entry.iterator();
		while (it.hasNext()) {
			temp += it.next().toString();
			if (it.hasNext()) { temp += ",\n"; }
		}
		temp += "\n]";
		return temp;
	}

}

