package aksis.alignment;

class QueueEntry implements Cloneable {

	Path path;   // a path of steps leading to a position
	float score = 0.f;   // the score for the path
	////String scoreHistory = "";   // ¤¤¤ foreløpig
	boolean removed = false;   // ...
	boolean end = false;   // if the path reaches the end of (all) the texts

	/*
	 * make queue entry with initial path
	 * #### skal klassen heller selv vite hvordan det første steget skal se ut? dvs -1, -1, med score 0
	 */
	QueueEntry(int[] position, float score) {
		//¤//System.out.println("QueueEntry(position, score) constructor. position=" + position[0] + "," + position[1] + ". score=" + score);
		path = new Path(position);
		//System.out.println("position -> path = " + path);
		this.score = score;
		//System.out.println("score = " + score);
		////scoreHistory = "Initiell score " + Integer.toString(score) + ". ";
		removed = false;   // 2005-11-01 aner ikke om vits i
		end = false;
	}

	// ¤¤¤ brukes visst ikke av clone()
	public Path getPath(){
		return path;
	}

	// brukes av clone()

	public void setPath(Path path){
		this.path = path;
	}

    public Object clone() {

        try {
			// first make exact bitwise copy
			QueueEntry copy = (QueueEntry)super.clone();
			// then copy the path
			copy.path = (Path)path.clone();   // Path has its own clone() method
			return copy;
        } catch (CloneNotSupportedException e) {
            throw new Error("This should not occur since we implement Cloneable");
        }

    }

	/*
	 * make a new queue entry with equal content to an existing entry,
	 * but with path extended with a particular step.
	 * ¤¤¤ used to be a constructor. not any more
	 */
	//QueueEntry(AlignmentModel model, QueueEntry queueEntry, PathStep newStep) {
	public QueueEntry makeLongerPath(AlignmentModel model, PathStep newStep) throws EndOfAllTextsException, EndOfTextException, BlockedException {

/*		System.out.println(">>>QueueEntry constructor 2. newStep = " + newStep);
		System.out.println(">>>enter makeLongerPath. score = " + score);*/
 		//System.out.println(">>>enter makeLongerPath. path = " + path);
 		//System.out.println(">>>enter makeLongerPath. newStep = " + newStep);

		QueueEntry retQueueEntry = (QueueEntry)this.clone();
 		//System.out.println(">>>makeLongerPath. har klonet. retQueueEntry sin score = " + retQueueEntry.score);
 		//System.out.println(">>>makeLongerPath. har klonet. retQueueEntry sin path = " + retQueueEntry.path);

		// but calculate new score before extending
		//System.out.println("QueueEntry constructor 2. newStep = " + newStep);
		//float stepScore;
		float newScore;
		try {
 			//System.out.println("før tryStep()");
			newScore = tryStep(model, newStep);
 			//System.out.println("tryStep() returnerer ny sti-skåre " + newScore);
		} catch (EndOfAllTextsException e) {
			//System.out.println("makeLongerPath() throws EndOfAllTextsException");
			throw e;   // ¤¤¤ er dette måten å forwarde en exception på?
		} catch (EndOfTextException e) {
			//System.out.println("makeLongerPath() throws EndOfTextException");
			throw e;   // ¤¤¤ er dette måten å forwarde en exception på?
		} catch (BlockedException e) {
			throw e;   // ¤¤¤ er dette måten å forwarde en exception på?
		}
		//score = queueEntry.score + stepScore;
		//retQueueEntry.score = this.score + stepScore;
		retQueueEntry.score = newScore;
		//System.out.println(">>>makeLongerPath. klonen retQueueEntry sin score økt med " + stepScore + " til " + retQueueEntry.score);
		//System.out.println(">>>makeLongerPath. klonen retQueueEntry sin score økt til " + retQueueEntry.score);
		////System.out.println("score øker med " + stepScore + " til " + score + " når vi tar steg " + newStep);
		//System.out.println("score øker med " + stepScore + " til " + retQueueEntry.score + " når vi tar steg " + newStep);
		////scoreHistory += "Score øker med " + stepScore + " til " + score + " når vi tar steg " + newStep.toString() + ". ";

		// extend.
		//System.out.println("path før extend = " + retQueueEntry.path);
		//System.out.println("skal utvide med steg " + newStep);
		//path.extend(newStep);
		retQueueEntry.path.extend(newStep);
		//System.out.println("path etter extend = " + retQueueEntry.path);

		//Object[] temp = {position, increment};
		//for (int t=0; t<Alignment.NUM_FILES; t++) {
		//	position[t] = queueEntry.position[t] + increments[t];   this
		//	System.out.println("position["+t+"]" + position[t]);
		//}

		// compare with old score for this position
		//System.out.println("compare with old score for this position. old score  = " + model.compare.getScore(model, path.position));
		//System.out.println("compare new score " + retQueueEntry.score + " with old score for this position. old score  = " + model.compare.getScore(model, this.path.position));
		//System.out.println("compare new score " + retQueueEntry.score + " with old score for this position. old score  = " + model.compare.getScore(model, retQueueEntry.path.position));
		//System.out.println("\n");
		//if (score > model.compare.getScore(model, path.position)) {
		if (retQueueEntry.score > model.compare.getScore(model, retQueueEntry.path.position)) {
			//System.out.println("new score beats old score");
			// new score beats old score.
			// update score and return the new QueueEntry object
			//System.out.println("position = " + path.position[0] + "," + path.position[1] + ". new score " + score + " beats old score " + model.compare.getScore(model, path.position));
			//model.compare.setScore(path.position, score);
			/*
			if ((retQueueEntry.path.position[0] > 73) && ((retQueueEntry.score == 13.0f) || (retQueueEntry.score == 14.0f) || (retQueueEntry.score == 15.0f))) {
				System.out.println("skal sette ny skåre 13 eller 14 eller 18: " + retQueueEntry.score + ". compare er nå\n" + model.compare);
			}
			*/
			model.compare.setScore(retQueueEntry.path.position, retQueueEntry.score);
			/*
			if ((retQueueEntry.path.position[0] > 73) && ((retQueueEntry.score == 13.0f) || (retQueueEntry.score == 14.0f) || (retQueueEntry.score == 15.0f))) {
				System.out.println("satte ny skåre 13 eller 14 eller 18. compare er nå\n" + model.compare);
			}
			*/
			//System.out.println("ny skåre satt. compare er nå\n" + model.compare);
			//¤//System.out.println(">>>QueueEntry constructor 2. ny og bedre skåre satt. utvidet path = " + this.path);
			//return;
			return retQueueEntry;
		} else {
			//System.out.println("new score not better than old score. returnerer med path = null");
			// new score not better than old score.
			// keep old score.
			// scrap the new QueueEntry object
			//¤//System.out.println("position = " + path.position[0] + "," + path.position[1] + ". new score " + score + " not better than old score " + model.compare.getScore(model, path.position));
			// ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ krøkkete
			//this = null;
			//this.path = null;
			retQueueEntry.path = null;
			//return;
			return retQueueEntry;
		}

	}

	// try to advance the current path one particular step
	// (i.e, increments of ¤¤¤)
	// and calculate new score for longer path

	float tryStep(AlignmentModel model, PathStep newStep) throws EndOfAllTextsException, EndOfTextException, BlockedException {

		//System.out.println("### tryStep. path = " + path);
		float stepScore = 0.f;
		try {
			stepScore = getStepScore(model, path.position, newStep);
		} catch (EndOfAllTextsException e) {
			//System.out.println("tryStep() throws EndOfAllTextsException");
			throw e;   // ¤¤¤ er dette måten å forwarde en exception på?
		} catch (EndOfTextException e) {
			//System.out.println("tryStep() throws EndOfTextException");
			throw e;   // ¤¤¤ er dette måten å forwarde en exception på?
		} catch (BlockedException e) {
			throw e;   // ¤¤¤ er dette måten å forwarde en exception på?
		}

		//System.out.println("### tryStep. score = " + score);
		//System.out.println("### tryStep. stepScore = " + stepScore);
		return score + stepScore;
	}

	float getStepScore(AlignmentModel model, int[] position, PathStep newStep) throws EndOfAllTextsException, EndOfTextException, BlockedException {

		//System.out.println("getStepScore(). position = " + position[0] + "," + position[1] + " , newStep = " + newStep);
		try {

			CompareCells compareCells = model.compare.getCellValues(model, position, newStep);

 			//System.out.println("getStepScore(). på slutten. kaller compareCells.elementInfoToBeCompared.getScore(), som gir " + compareCells.elementInfoToBeCompared.getScore());
			return compareCells.elementInfoToBeCompared.getScore();

		} catch (EndOfAllTextsException e) {
 			//System.out.println("getStepScore() throws EndOfAllTextsException");
			throw e;   // ¤¤¤ er dette måten?
		} catch (EndOfTextException e) {
 			//System.out.println("getStepScore() throws EndOfTextException");
			throw e;   // ¤¤¤ er dette måten?
		}

	}

	public void remove() {
		// mark as removed
		removed = true;
	}

	public void end() {
		// mark as path that reaches the end of the texts
		end = true;
	}

	public String toString() {
		String temp = "";
		if (removed) {
			temp += "(removed) ";
		}
		if (end) {
			temp += "(end) ";
		}
		temp += "position = {";
		for (int t=0; t<Alignment.NUM_FILES; t++) {
			if (t > 0) { temp += ","; }
			//System.out.println("QueueEntry sin toString(). path = " + path);
			temp += Integer.toString(path.position[t]);
		}
		temp += "}\n";
		temp += "path = " + path.toString();
		temp += ", score = " + Float.toString(score);
		////temp += "scoreHistory = " + scoreHistory + "\n";
		return temp;
	}

}

