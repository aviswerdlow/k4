{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\froman\fcharset0 Times-Bold;\f1\froman\fcharset0 Times-Italic;\f2\froman\fcharset0 Times-BoldItalic;
\f3\froman\fcharset0 Times-Roman;\f4\fmodern\fcharset0 Courier;}
{\colortbl;\red255\green255\blue255;\red0\green0\blue0;\red109\green109\blue109;}
{\*\expandedcolortbl;;\cssrgb\c0\c0\c0;\cssrgb\c50196\c50196\c50196;}
{\*\listtable{\list\listtemplateid1\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid1\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid1}
{\list\listtemplateid2\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid101\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid2}
{\list\listtemplateid3\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid201\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid3}
{\list\listtemplateid4\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid301\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid4}
{\list\listtemplateid5\listhybrid{\listlevel\levelnfc0\levelnfcn0\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{decimal\}}{\leveltext\leveltemplateid401\'01\'00;}{\levelnumbers\'01;}\fi-360\li720\lin720 }{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{circle\}}{\leveltext\leveltemplateid402\'01\uc0\u9702 ;}{\levelnumbers;}\fi-360\li1440\lin1440 }{\listname ;}\listid5}
{\list\listtemplateid6\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid501\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid6}
{\list\listtemplateid7\listhybrid{\listlevel\levelnfc0\levelnfcn0\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{decimal\}}{\leveltext\leveltemplateid601\'01\'00;}{\levelnumbers\'01;}\fi-360\li720\lin720 }{\listname ;}\listid7}
{\list\listtemplateid8\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid701\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid8}
{\list\listtemplateid9\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid801\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid9}}
{\*\listoverridetable{\listoverride\listid1\listoverridecount0\ls1}{\listoverride\listid2\listoverridecount0\ls2}{\listoverride\listid3\listoverridecount0\ls3}{\listoverride\listid4\listoverridecount0\ls4}{\listoverride\listid5\listoverridecount0\ls5}{\listoverride\listid6\listoverridecount0\ls6}{\listoverride\listid7\listoverridecount0\ls7}{\listoverride\listid8\listoverridecount0\ls8}{\listoverride\listid9\listoverridecount0\ls9}}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\sa321\partightenfactor0

\f0\b\fs48 \cf0 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 The Survey Traverse Algorithm\
\pard\pardeftab720\sa240\partightenfactor0

\f1\i\b0\fs24 \cf0 (from Flint & Gillet, 
\f2\b A System of Geometry and Trigonometry; with a Treatise on Surveying
\f1\b0 , 8th ed.)
\f3\i0 \
\pard\pardeftab720\sa240\partightenfactor0

\f0\b \cf0 Scope.
\f3\b0  This spec extracts the literal, step\uc0\u8209 by\u8209 step procedure for running a full survey traverse the way Flint & Gillet prescribe: from first observation through closure/balance, and then area by rectangular (coordinate) computation. It also isolates the book\'92s \'93key\u8209 schedule\u8209 like\'94 sequence for using the 
\f0\b Traverse Table
\f3\b0  (table of \'93Difference of Latitude and Departure\'94). All phrases and rules below are grounded in the Treatise; page/figure cues and verbatim phrasings are cited inline.\
\pard\pardeftab720\partightenfactor0
\cf3 \strokec3 \
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 \strokec2 0) Instruments, meridian, and variation (setup)\
\pard\pardeftab720\sa240\partightenfactor0

\fs24 \cf0 0.1 Choose a working meridian and account for variation (declination).
\f3\b0 \uc0\u8232 The Treatise gives a practical method for finding magnetic variation from the North Star (Polaris) using Alioth/Cassiopeia alignments and a small table of elongations. Use this to establish the relationship between compass north and the true meridian before you take courses/bearings.\
\pard\pardeftab720\partightenfactor0
\cf3 \strokec3 \
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 \strokec2 1) Field work: courses, distances, and the Field\uc0\u8209 Book\
\pard\pardeftab720\sa240\partightenfactor0

\fs24 \cf0 1.1 Run the boundary in order and keep a Field\uc0\u8209 Book.
\f3\b0 \uc0\u8232 A 
\f1\i Field\uc0\u8209 Book
\f3\i0  is \'93a register containing the length of the sides of a field\'85 also the bearings or courses of the sides\'85 together with such remarks as the surveyor thinks proper to make in the field.\'94 Record each side 
\f0\b in order
\f3\b0  with its quadrant bearing (e.g., 
\f1\i N 27\'b0 45\uc0\u8242  W
\f3\i0 ) and its length (chains, links; or rods and decimals).\

\f0\b 1.2 Sample layout and content.
\f3\b0 \uc0\u8232 The Treatise prints a model Field\u8209 Book (Fig. 61) with columns for 
\f1\i Bearing and distance
\f3\i0 , 
\f1\i Offsets to the left/right
\f3\i0 , and 
\f1\i Remarks
\f3\i0  (e.g., intervisible objects, inaccessible corners). Use the same headings and notations.\
\pard\pardeftab720\sa240\partightenfactor0

\f0\b \cf0 Note (good practice).
\f3\b0  Because of local attractions, \'93the compass should be set at least twice on each line\'85 enter a medium course\'85 prefix \'b1 when you suspect minutes may be added/subtracted; this often assists in balancing.\'94\
\pard\pardeftab720\partightenfactor0
\cf3 \strokec3 \
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 \strokec2 2) Build the Traverse Table (the computation sheet)\
\pard\pardeftab720\sa240\partightenfactor0

\fs24 \cf0 2.1 Transcribe to a traverse table.
\f3\b0 \uc0\u8232 From the Field\u8209 Book, set down (verbatim) the 
\f0\b course/bearing
\f3\b0  and 
\f0\b length
\f3\b0  for each side in the traverse table\'92s first columns; Flint & Gillet explicitly instruct this as Step 
\f1\i I
\f3\i0  of \'93Rectangular Surveying\'85 without plotting.\'94\

\f0\b 2.2 Compute or look up coordinates for each course (\'93latitude & departure\'94).
\f3\b0 \uc0\u8232 For each side, obtain its 
\f0\b northing or southing
\f3\b0  (difference of latitude) and 
\f0\b easting or westing
\f3\b0  (departure) by 
\f1\i either
\f3\i0 :\
\pard\tx220\tx720\pardeftab720\li720\fi-720\sa240\partightenfactor0
\ls1\ilvl0
\f0\b \cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Right\uc0\u8209 angled trigonometry (Case I)
\f3\b0 ; 
\f1\i or
\f3\i0 \
\ls1\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 The Table of Difference of Latitude and Departure (Traverse Table)
\f3\b0 ; 
\f1\i or
\f3\i0 \
\ls1\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 The Table of Natural Sines
\f3\b0 .\uc0\u8232 Then \'93set them down against their several courses in their proper columns, marked 
\f0\b N. S. E. W.
\f3\b0 \'94 This is Step 
\f1\i 2
\f3\i0  in the Treatise.\
\pard\pardeftab720\partightenfactor0
\cf3 \strokec3 \
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 \strokec2 3) The Traverse Table \'93Key Schedule\'94 (literal usage order)\
\pard\pardeftab720\sa240\partightenfactor0

\f3\b0\fs24 \cf0 The Treatise gives a deterministic sequence for using the Traverse Table\'97effectively a fixed schedule of look\uc0\u8209 ups and sign assignments:\
\pard\pardeftab720\sa240\partightenfactor0

\f0\b \cf0 3.1 Where to read on each page.
\f3\b0 \
\pard\tx220\tx720\pardeftab720\li720\fi-720\sa240\partightenfactor0
\ls2\ilvl0\cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 \'93If the course be 
\f0\b less than 45\'b0
\f3\b0 , look for it 
\f0\b at the top
\f3\b0 ;\
\ls2\ilvl0\kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 If 
\f0\b more than 45\'b0
\f3\b0 , 
\f0\b at the bottom
\f3\b0  of the page.\'94\uc0\u8232 On the 
\f0\b top line
\f3\b0 , 
\f0\b read from left to right
\f3\b0 ; on the 
\f0\b bottom line
\f3\b0 , 
\f0\b from right to left
\f3\b0 .\
\pard\pardeftab720\sa240\partightenfactor0

\f0\b \cf0 3.2 What the two numbers are called.
\f3\b0 \uc0\u8232 \'93The least of the two distances is called the 
\f0\b departure
\f3\b0 ; and the greatest the 
\f0\b difference of latitude
\f3\b0 .\'94 (I.e., |sin| vs |cos| scaled by the distance.)\

\f0\b 3.3 How to scale by distance.
\f3\b0 \uc0\u8232 For the length actually run, \'93the 
\f0\b difference of latitude
\f3\b0  and 
\f0\b departure
\f3\b0 \'85 are obtained 
\f0\b by proportion
\f3\b0  from the table.\'94 (Multiply table values by the observed distance, observing the chain/link or rod units in use.)\

\f0\b 3.4 How to assign signs (quadrants).
\f3\b0 \uc0\u8232 \'93
\f0\b Difference of latitude
\f3\b0  lies 
\f0\b north or south
\f3\b0  according to the 
\f0\b bearing\'92s first letter
\f3\b0  (N/S); 
\f0\b departure
\f3\b0  lies 
\f0\b east or west
\f3\b0  according to the 
\f0\b second letter
\f3\b0  (E/W).\'94\
\pard\pardeftab720\sa240\partightenfactor0

\f0\b \cf0 Operational invariant.
\f3\b0  Execute 3.1 \uc0\u8594  3.4 for 
\f1\i each
\f3\i0  side in order. This fixed top/bottom, L\uc0\u8594 R/R\u8594 L page traversal\'97plus the N/S/E/W sign\u8209 assignment rule\'97acts like a 
\f0\b key schedule
\f3\b0  you repeat once per side.\
\pard\pardeftab720\partightenfactor0
\cf3 \strokec3 \
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 \strokec2 4) First closure test (raw sums)\
\pard\pardeftab720\sa240\partightenfactor0

\fs24 \cf0 4.1 Sum checks.
\f3\b0 \uc0\u8232 After you fill the N/S/E/W columns:\
\pard\tx220\tx720\pardeftab720\li720\fi-720\sa240\partightenfactor0
\ls3\ilvl0\cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 \'93The 
\f0\b sum of the northings
\f3\b0  should equal the 
\f0\b sum of the southings
\f3\b0 ;\
\ls3\ilvl0\kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 The 
\f0\b sum of the eastings
\f3\b0  should equal the 
\f0\b sum of the westings
\f3\b0 .\'94\
\pard\pardeftab720\sa240\partightenfactor0

\f0\b \cf0 4.2 If unequal (diagnose vs. accept and correct).
\f3\b0 \uc0\u8232 If not equal, \'93the surveyor must have committed [an error]\'85 if the difference be great he must 
\f0\b run over his work again
\f3\b0 ; but if it be small\'85 it will 
\f0\b necessarily
\f3\b0  arise\'85 every time the survey is gone over.\'94\
\pard\pardeftab720\partightenfactor0
\cf3 \strokec3 \
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 \strokec2 5) Balancing (\'93closure/balance\'94)\
\pard\pardeftab720\sa240\partightenfactor0

\fs24 \cf0 5.1 Balancing rule (when differences are small).
\f3\b0 \uc0\u8232 The Treatise demonstrates distributing the small residuals so the traverse 
\f0\b closes
\f3\b0 : one example shows 
\f1\i equally dividing
\f3\i0  the difference of northings/southings and then applying a corresponding correction on departures (\'93as it was judged that sufficient distances were made on the two westerly courses, the correction was made on the 
\f0\b eastings
\f3\b0 \'94).\

\f0\b 5.2 Per\uc0\u8209 line reasonableness.
\f3\b0 \uc0\u8232 The Appendix also gives a line\u8209 by\u8209 line reasonableness check: for a right\u8209 angle turn, verify 
\f0\b distance\'b2 = northing\'b2 + easting\'b2
\f3\b0 , and analogs for successive legs (a \'93Pythagorean\'94 spot\uc0\u8209 check).\
\pard\pardeftab720\sa240\partightenfactor0

\f0\b \cf0 Outcome.
\f3\b0  After balancing, your N/S and E/W column totals should match pairwise (zero misclosure), i.e., the traverse 
\f0\b closes
\f3\b0  arithmetically.\
\pard\pardeftab720\partightenfactor0
\cf3 \strokec3 \
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 \strokec2 6) Meridian placement and the Meridian Flip\
\pard\pardeftab720\sa240\partightenfactor0

\f3\b0\fs24 \cf0 Once the traverse balances, Flint & Gillet compute 
\f0\b area
\f3\b0  using 
\f0\b meridian distances
\f3\b0  (accumulated x\uc0\u8209 coordinates). Where you place the meridian (east or west side of the figure) 
\f0\b changes the sign logic
\f3\b0 \'97i.e., a literal \'93meridian flip.\'94\
\pard\pardeftab720\sa240\partightenfactor0

\f0\b \cf0 6.1 Choose the meridian side.
\f3\b0 \uc0\u8232 Draw the meridian \'93at the 
\f0\b eastern
\f3\b0  extremity\'94 
\f1\i or
\f3\i0  \'93on the 
\f0\b west
\f3\b0  side\'94 of the tract. This is at your discretion; it only changes how you add/subtract departures in the next step.\

\f0\b 6.2 Form the 
\f2\i Meridian Distance
\f0\i0  column (cumulative x).
\f3\b0 \uc0\u8232 The rule is explicit and opposite depending on your choice:\
\pard\tx220\tx720\pardeftab720\li720\fi-720\sa240\partightenfactor0
\ls4\ilvl0
\f0\b \cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 If the meridian is at the 
\f2\i eastern
\f0\i0  extremity
\f3\b0 :\uc0\u8232 
\f0\b Add
\f3\b0  all 
\f0\b westings
\f3\b0  and 
\f0\b subtract
\f3\b0  all 
\f0\b eastings
\f3\b0  as you proceed down the lines to build the cumulative 
\f0\b Meridian Distance
\f3\b0  column.\
\ls4\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 If the meridian is at the 
\f2\i western
\f0\i0  extremity
\f3\b0  (
\f0\b meridian flip
\f3\b0 ):\uc0\u8232 
\f0\b Add
\f3\b0  all 
\f0\b eastings
\f3\b0  and 
\f0\b subtract
\f3\b0  all 
\f0\b westings
\f3\b0  while forming Meridian Distances.\
\pard\pardeftab720\sa240\partightenfactor0

\f0\b \cf0 6.3 Double\uc0\u8209 Mean Distances (D.M.D.).
\f3\b0 \uc0\u8232 For each side, \'93the 
\f0\b meridian distance proceeding from each end of a line are added
\f3\b0 \'94 to form the 
\f0\b Double Mean Distance
\f3\b0  for that line.\

\f0\b 6.4 Areas by latitudes & meridian distances.
\f3\b0 \uc0\u8232 Multiply each line\'92s 
\f0\b D.M.D.
\f3\b0  by its 
\f0\b northing or southing
\f3\b0  (difference of latitude) to obtain a 
\f0\b North Area
\f3\b0  or 
\f0\b South Area
\f3\b0  entry. Sum the North Areas and South Areas; 
\f0\b their difference is the area
\f3\b0  (convert to acres/rods as needed).\
\pard\pardeftab720\partightenfactor0
\cf3 \strokec3 \
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 \strokec2 7) End\uc0\u8209 to\u8209 end algorithm (normative checklist)\
\pard\pardeftab720\sa240\partightenfactor0

\fs24 \cf0 INPUTS:
\f3\b0  Field\uc0\u8209 Book entries (ordered sides with bearing & length), unit convention (chains/links or rods/decimals), chosen meridian side, Traverse Table access.\u8232 
\f0\b OUTPUTS:
\f3\b0  Balanced N/S/E/W columns, Meridian Distances, D.M.D., Area; closure diagnostics.\
\pard\tx220\tx720\pardeftab720\li720\fi-720\sa240\partightenfactor0
\ls5\ilvl0
\f0\b \cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	1	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Variation & Meridian.
\f3\b0  Establish declination/variation; select a working meridian (east or west side).\
\ls5\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	2	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Field\uc0\u8209 Book.
\f3\b0  Record each side\'92s quadrant bearing and distance; include offsets/remarks where needed.\
\ls5\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	3	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Traverse Table setup.
\f3\b0  Copy bearings & distances as the traverse table\'92s first columns.\
\ls5\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	4	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Per\uc0\u8209 side look\u8209 up (key schedule):
\f3\b0 \uc0\u8232 a. Bearing < 45\'b0 \u8594  read 
\f0\b top
\f3\b0  line 
\f0\b L\uc0\u8594 R
\f3\b0 ; > 45\'b0 \uc0\u8594  
\f0\b bottom
\f3\b0  line 
\f0\b R\uc0\u8594 L
\f3\b0 .\uc0\u8232 b. The 
\f0\b greater
\f3\b0  value is 
\f0\b difference of latitude
\f3\b0 , the 
\f0\b lesser
\f3\b0  is 
\f0\b departure
\f3\b0 ; scale by the line\'92s length.\uc0\u8232 c. Assign signs by letters: 
\f0\b N/S
\f3\b0  from the first letter; 
\f0\b E/W
\f3\b0  from the second.\uc0\u8232 d. Write the signed values into 
\f0\b N/S/E/W
\f3\b0  columns.\
\ls5\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	5	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 First closure test.
\f3\b0  Check \uc0\u931 N = \u931 S and \u931 E = \u931 W. If large error \u8594  re\u8209 survey; if small \u8594  balance.\
\ls5\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	6	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Balance.
\f3\b0  Adjust small residuals (e.g., split north/south misclosure equally; apply corresponding departure fix where justified) until both pairs of sums match. Spot\uc0\u8209 check with right\u8209 triangle tests where applicable.\
\ls5\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	7	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Meridian distances (flip\uc0\u8209 aware).
\f3\b0 \
\pard\tx940\tx1440\pardeftab720\li1440\fi-1440\sa240\partightenfactor0
\ls5\ilvl1\cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u9702 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 If 
\f0\b eastern meridian
\f3\b0 : 
\f0\b add W
\f3\b0 , 
\f0\b subtract E
\f3\b0  cumulatively.\
\ls5\ilvl1\kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u9702 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 If 
\f0\b western meridian
\f3\b0 : 
\f0\b add E
\f3\b0 , 
\f0\b subtract W
\f3\b0  cumulatively.\uc0\u8232 Record the resulting 
\f0\b Meridian Distance
\f3\b0  for each line.\
\pard\tx220\tx720\pardeftab720\li720\fi-720\sa240\partightenfactor0
\ls5\ilvl0
\f0\b \cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	8	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Double\uc0\u8209 Mean Distances.
\f3\b0  For each line, 
\f0\b add
\f3\b0  the meridian distances at its two ends \uc0\u8594  
\f0\b D.M.D.
\f3\b0 \
\ls5\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	9	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Areas by latitude.
\f3\b0  Multiply each line\'92s 
\f0\b D.M.D.
\f3\b0  by that line\'92s 
\f0\b northing/southing
\f3\b0  to make 
\f0\b North Areas
\f3\b0  or 
\f0\b South Areas
\f3\b0 . Sum each; 
\f0\b difference = area
\f3\b0  of the field.\
\ls5\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	10	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Final checks & report.
\f3\b0  Confirm all totals (unit conversions to acres/roods/rods if using chains/links), and deliver the balanced table and resulting area.\
\pard\pardeftab720\partightenfactor0
\cf3 \strokec3 \
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 \strokec2 8) Pseudocode (faithful to the Treatise)\
\pard\pardeftab720\partightenfactor0

\f4\b0\fs26 \cf0 Given lines i = 1..m with (bearing_i, dist_i)\
\
# 1) Per-line coordinates via Traverse Table\
for i in 1..m:\
  if bearing_i < 45\'b0: read top row left\uc0\u8594 right else: read bottom row right\u8594 left\
  (lat_unit, dep_unit) \uc0\u8592  table(bearing_i)   # greater=lat, lesser=dep\
  lat_i \uc0\u8592  lat_unit * dist_i\
  dep_i \uc0\u8592  dep_unit * dist_i\
  sign(lat_i) \uc0\u8592  + if first letter is N else \u8722  (if S)\
  sign(dep_i) \uc0\u8592  + if second letter is E else \u8722  (if W)\
  accumulate columns N/S/E/W accordingly\
\
# 2) Closure & balance (apply small corrections until \uc0\u931 N=\u931 S and \u931 E=\u931 W)\
\
# 3) Meridian flip & meridian distances\
if meridian_side == "EAST":\
  rule: MD_k = MD_\{k-1\} + W_k \uc0\u8722  E_k\
else:  # WEST\
  rule: MD_k = MD_\{k-1\} + E_k \uc0\u8722  W_k\
\
# 4) Double-Mean Distances & areas\
for each line k with endpoints (k\uc0\u8722 1, k):\
  DMD_k = MD_\{k-1\} + MD_k\
  if lat_k > 0: NorthArea += DMD_k * lat_k else SouthArea += DMD_k * |lat_k|\
\
Area = |NorthArea \uc0\u8722  SouthArea|\
\pard\pardeftab720\sa240\partightenfactor0

\f3\fs24 \cf0 This is a direct transcription of the book\'92s operations: page direction on table lookup; N/S/E/W sign rules; meridian\uc0\u8209 dependent accumulation; double\u8209 mean distance products.\
\pard\pardeftab720\partightenfactor0
\cf3 \strokec3 \
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 \strokec2 9) Where the algorithm changes branch (the built\uc0\u8209 in \'93triggers\'94)\
\pard\tx220\tx720\pardeftab720\li720\fi-720\sa240\partightenfactor0
\ls6\ilvl0
\fs24 \cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Table reading direction trigger:
\f3\b0  
\f1\i If
\f3\i0  course < 45\'b0 \uc0\u8594  
\f0\b top/L\uc0\u8594 R
\f3\b0 ; 
\f1\i if
\f3\i0  > 45\'b0 \uc0\u8594  
\f0\b bottom/R\uc0\u8594 L
\f3\b0 .\
\ls6\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Sign assignment trigger:
\f3\b0  
\f1\i If
\f3\i0  first letter is 
\f0\b N/S
\f3\b0  \uc0\u8594  latitude sign; 
\f1\i if
\f3\i0  second letter is 
\f0\b E/W
\f3\b0  \uc0\u8594  departure sign.\
\ls6\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Closure trigger:
\f3\b0  
\f1\i If
\f3\i0  \uc0\u931 N\u8800 \u931 S or \u931 E\u8800 \u931 W \u8594  
\f1\i then
\f3\i0  re\uc0\u8209 observe (if large) or balance (if small).\
\ls6\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Meridian flip trigger:
\f3\b0  
\f1\i If
\f3\i0  meridian at 
\f0\b east
\f3\b0  edge \uc0\u8594  
\f1\i (+W, \uc0\u8722 E)
\f3\i0 ; 
\f1\i if
\f3\i0  at 
\f0\b west
\f3\b0  edge \uc0\u8594  
\f1\i (+E, \uc0\u8722 W)
\f3\i0  for forming MD column.\
\pard\pardeftab720\partightenfactor0
\cf3 \strokec3 \
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 \strokec2 10) Minimal working example (columns you should produce)\
\pard\pardeftab720\sa240\partightenfactor0

\f3\b0\fs24 \cf0 Your final traverse sheet should contain 
\f0\b at least
\f3\b0  these columns (matching the book\'92s examples):\
\pard\tx220\tx720\pardeftab720\li720\fi-720\sa240\partightenfactor0
\ls7\ilvl0
\f0\b \cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	1	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Course/Bearing
\f3\b0 , 2) 
\f0\b Distance
\f3\b0 , 3\'966) 
\f0\b N/S/E/W
\f3\b0  (balanced), 7) 
\f0\b Meridian Distance
\f3\b0 , 8) 
\f0\b Double Mean Distance
\f3\b0 , 9\'9610) 
\f0\b North Areas / South Areas
\f3\b0 , and the final 
\f0\b Area
\f3\b0  as |\uc0\u931 North Areas \u8722  \u931 South Areas| with unit conversion to acres/roods/rods if working in chains/links. Compare to the worked tables and notes across pp. 112\'96115 and the Field\u8209 Book figure on p. 63.\
\pard\pardeftab720\partightenfactor0
\cf3 \strokec3 \
\pard\pardeftab720\sa280\partightenfactor0

\f0\b\fs28 \cf0 \strokec2 Appendix: Page anchors for operators\
\pard\tx220\tx720\pardeftab720\li720\fi-720\sa240\partightenfactor0
\ls8\ilvl0
\fs24 \cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Rectangular Surveying\'97Step I/II/III (the backbone):
\f3\b0  how to set the traverse table, compute N/S/E/W, and check closure.\
\ls8\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Traverse Table usage (top vs bottom; L\uc0\u8594 R vs R\u8594 L; naming & signs):
\f3\b0  the deterministic \'93key schedule.\'94\
\ls8\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Meridian Distance & Double\uc0\u8209 Mean Distance area method (and the flip):
\f3\b0  how to add/subtract E/W by meridian side, then form D.M.D. and areas.\
\ls8\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Field\uc0\u8209 Book model & definition:
\f3\b0  what to record in the field and how it\'92s laid out.\
\ls8\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Variation by Polaris (meridian establishment):
\f3\b0  practical setup before courses.\
\pard\pardeftab720\partightenfactor0
\cf3 \strokec3 \
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 \strokec2 Why this reads like a master algorithm\
\pard\tx220\tx720\pardeftab720\li720\fi-720\sa240\partightenfactor0
\ls9\ilvl0
\f3\b0\fs24 \cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 It 
\f0\b iterates
\f3\b0  the same fixed schedule per side (table page choice \uc0\u8594  read direction \u8594  scale \u8594  assign signs).\
\ls9\ilvl0\kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 It has 
\f0\b explicit branch points
\f3\b0  (\'93if/when\'94 conditions) that change computational flow (table top/bottom at 45\'b0, sign from initial letters, closure thresholds, meridian flip).\
\ls9\ilvl0\kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 It 
\f0\b accumulates state
\f3\b0  (meridian distances; D.M.D.), culminating in a 
\f0\b final check
\f3\b0  (\uc0\u931 N=\u931 S, \u931 E=\u931 W; area difference).\
\pard\pardeftab720\sa240\partightenfactor0
\cf0 These are precisely the kinds of deterministic, pencil\uc0\u8209 and\u8209 paper control\u8209 flow elements that can be mapped to a cryptographic 
\f0\b key schedule
\f3\b0  or clock\uc0\u8209 and\u8209 selector framework.\
\pard\pardeftab720\partightenfactor0
\cf3 \strokec3 \
\pard\pardeftab720\sa280\partightenfactor0

\f0\b\fs28 \cf0 \strokec2 Ready\uc0\u8209 to\u8209 use deliverable\
\pard\pardeftab720\sa240\partightenfactor0

\f3\b0\fs24 \cf0 If you want this as a one\uc0\u8209 page handout for the team (\'93operator spec\'94) or as a CSV header template for the Apprentice\'92s sheets, say the word and I\'92ll output both immediately with the exact column order above.\
}