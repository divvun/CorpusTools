/*
 * MemTest.java
 *
 * ...
 * ...
 * @author Oystein Reigem
 */

package aksis.alignment;

//import javax.management.*;
import java.lang.management.*;
import java.util.*;

public class MemTest {

	// from <http://www.roseindia.net/javatutorials/OutOfMemoryError_Warning_System.shtml>
	private static final MemoryPoolMXBean tenuredGenPool = findTenuredGenPool();
	/**
	 * Tenured Space Pool can be determined by it being of type
	 * HEAP and by it being possible to set the usage threshold.
	 */
	private static MemoryPoolMXBean findTenuredGenPool() {
		for (MemoryPoolMXBean pool : ManagementFactory.getMemoryPoolMXBeans()) {
			// I don't know whether this approach is better, or whether
			// we should rather check for the pool name "Tenured Gen"?
			if (pool.getType() == MemoryType.HEAP && pool.isUsageThresholdSupported()) {
				return pool;
			}
		}
		throw new AssertionError("Could not find tenured space");
	}

/*
From here on, functions used by non gui code
*/
    // returns remaining heap space (??????????) in bytes
    public static long getRemainingHeap() {
        // from <http://www.roseindia.net/javatutorials/OutOfMemoryError_Warning_System.shtml>
        long maxMemory = tenuredGenPool.getUsage().getMax();
        long usedMemory = tenuredGenPool.getUsage().getUsed();

        return maxMemory - usedMemory;
    }

    public static long[] getMemoryUsage() {
        //System.out.println("MemTest sin getMemoryUsage()");
        // 2010-08-30
        long[] array = new long[2];
        // set default values in case the code below
        // fails to find information about memory use.
        // such failure has been observed on newer platforms.
        // ###at failure now the user will be told that usage is 0 out of max 0,
        // which of course is somewhat misleading...
        array[0] = 0;
        array[1] = 0;
        // end 2010-08-30

        // 2010-10-13
        long maxMemory = tenuredGenPool.getUsage().getMax();
        //System.out.println("maxMemory = " + maxMemory);
        long usedMemory = tenuredGenPool.getUsage().getUsed();
        //System.out.println("usedMemory = " + usedMemory);
        array[0] = maxMemory;
        array[1] = usedMemory;
        
        return array;   // 2010-08-30
    }
}
