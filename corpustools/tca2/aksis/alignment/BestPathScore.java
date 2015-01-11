package aksis.alignment;

class BestPathScore {

	private float score;

	public BestPathScore() {
		//score = Float.MIN_VALUE;
		//score = -1.0f;   // 2005-08-23. varianten over var sikkert også ok, men hadde stått utkommentert lenge. uten disse fikk jeg initiell verdi 0.0, som nye stier med skåre 0.0 tapte mot
		score = AlignmentModel.BEST_PATH_SCORE_NOT_CALCULATED;   // 2006-09-20
	}

	public BestPathScore(float score) {
		//score = Float.MIN_VALUE;
		this.score = score;
	}

	public float getScore() {
		return score;
	}

	public String toString() {
		return "" + score;
	}

}

