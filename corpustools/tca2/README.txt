To compile issue this command:

ant
After the build has completed the .class files can be found in build/aksis/alignment map.
The jar file is found in dist/lib map, with the name alignment-<date-when-built>.jar

To remove old jar files and .class files, use the command:
ant clean

Java 1.5 issues some warnings on this code. To get more detail about what's
wrong, use this command:
	javac -Xlint:unchecked aksis/alignment/*.java

tca2 has a cli and a gui mode as of 20110518

The anchor file is made as follows:



To run it in gui mode, issue this command:
java -jar dist/lib/alignment.jar

To load files when starting tca2 in gui mode, issue this command:
(note that you must have absolute paths to the files, no tilde notation)

java -jar dist/lib/alignment.jar -anchor=<anchorfilename> -in1=<thefirstfileofapairtoalign> -in2=<thesecondfileofapairtoalign>

To run in in cli mode, issue this command:
java -jar dist/lib/alignment.jar -cli -anchor=<anchorfilename> -in1=<thefirstfileofapairtoalign> -in2=<thesecondfileofapairtoalign>

There also exists a helper shell file in $GTHOME/gt/script/tca2.sh, which expects to find a jar file called alignment.jar in $GTHOME/tools/alignment-tools/tca2/dist/lib/alignment.jar. It is called this way:
tca2.sh <anchorfilename> <thefirstfileofapairtoalign> <thesecondfileofapairtoalign>

