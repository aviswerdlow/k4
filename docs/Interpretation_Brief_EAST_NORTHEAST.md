{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 HelveticaNeue-Bold;\f1\fnil\fcharset0 .SFNS-Regular;\f2\fnil\fcharset0 .SFNS-RegularItalic;
\f3\fnil\fcharset0 HelveticaNeue-BoldItalic;}
{\colortbl;\red255\green255\blue255;\red14\green14\blue14;}
{\*\expandedcolortbl;;\cssrgb\c6700\c6700\c6700;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\sl324\slmult1\pardirnatural\partightenfactor0

\f0\b\fs32 \cf2 Interpretation Brief \'97 \'93EAST NORTHEAST\'94 (Flint & Gillet, 1841)
\f1\b0 \
\

\f0\b Ruling (actionable):
\f1\b0 \
Read 
\f0\b EAST NORTHEAST
\f1\b0  as a single bearing: 
\f0\b NORTHEAST (NE)
\f1\b0 \'97i.e., 
\f2\i N 45\'b0 E
\f1\i0  in the book\'92s magnetic frame. It is 
\f0\b not
\f1\b0  the mariner\'92s point 
\f0\b ENE (67.5\'b0)
\f1\b0 , 
\f0\b not
\f1\b0  two separate bearings, and 
\f0\b not
\f1\b0  a separate idiom in the Treatise.\
\

\f0\b Why this is the only reading consistent with the Treatise
\f1\b0 \
\pard\tqr\tx280\tx440\li440\fi-440\sl324\slmult1\sb240\partightenfactor0
\cf2 	1.	
\f0\b How the Treatise writes bearings.
\f1\b0  Flint & Gillet state that survey courses are expressed as 
\f0\b quadrantal bearings
\f1\b0 : \'93
\f2\i Courses are counted either east or west from their respective meridians\'85 the angle\'85 is written 
\f3\b north or south, so many degrees east or west
\f1\i0\b0 ,\'94 with worked examples \'93
\f0\b N. 40\'b0 E.
\f1\b0  \'85 
\f0\b S. 80\'b0 W.
\f1\b0  \'85 
\f0\b N. 80\'b0 E.
\f1\b0  
\f2\i In like manner take all other courses
\f1\i0 .\'94 This house\uc0\u8209 style leaves no role for named 32\u8209 point compass terms such as \'93east\u8209 northeast.\'94  \
	2.	
\f0\b Vocabulary in context.
\f1\b0  When the authors refer to direction in words, they use broad quadrant descriptors (\'93
\f2\i southeasterly
\f1\i0 ,\'94 \'93
\f2\i southwesterly
\f1\i0 \'94), not intermediate point names; the measurement itself is always given as 
\f0\b N/S \uc0\u952  E/W
\f1\b0  degrees.  \
	3.	
\f0\b Implication.
\f1\b0  If an intermediate direction like \'93east\uc0\u8209 northeast\'94 were intended, the Treatise\'92s form would be 
\f0\b N 67\'b030\uc0\u8242  E
\f1\b0  (or 
\f0\b E 22\'b030\uc0\u8242  N
\f1\b0 ), not the phrase 
\f2\i east northeast
\f1\i0 . Therefore the only text\uc0\u8209 faithful interpretation of the plaintext token 
\f0\b EAST NORTHEAST
\f1\b0  is 
\f0\b NE = 45\'b0
\f1\b0  in the magnetic frame used by the book.  \
\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\sl324\slmult1\pardirnatural\partightenfactor0

\f0\b \cf2 Operational guidance for The Architect
\f1\b0 \
\pard\tqr\tx100\tx260\li260\fi-260\sl324\slmult1\sb240\partightenfactor0
\cf2 	\'95	
\f0\b Parser rule:
\f1\b0  When the plaintext contains the contiguous phrase 
\f0\b \'93EAST NORTHEAST\'94
\f1\b0  (with or without a hyphen), treat it as 
\f0\b one direction token = NORTHEAST
\f1\b0 .\
	\'95	
\f0\b Downstream math:
\f1\b0  In Flint & Gillet\'92s workflow, bearings are then handled as 
\f0\b N/S \uc0\u952  E/W
\f1\b0 . If you are applying the team\'92s east variation to convert to the true meridian, add the variation to the magnetic azimuth before reducing to latitude/departure (per the Treatise\'92s practice). The team\'92s current run (NE + 16.6959\'b0 E) rightly yields a true bearing of 
\f0\b N 61.6959\'b0 E
\f1\b0 .  \
\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\sl324\slmult1\pardirnatural\partightenfactor0

\f0\b \cf2 What it is not
\f1\b0 \
\pard\tqr\tx100\tx260\li260\fi-260\sl324\slmult1\sb240\partightenfactor0
\cf2 	\'95	
\f0\b Not two instructions.
\f1\b0  The Treatise would separate distinct courses by distance entries in the field\uc0\u8209 book style; a single run\u8209 on phrase without a separator is not two legs. (See the book\'92s field\u8209 book and course examples for how multi\u8209 leg instructions are actually written.)  \
	\'95	
\f0\b Not ENE (67.5\'b0).
\f1\b0  The Treatise never uses 32\uc0\u8209 point names to direct a course; it always specifies degrees from a meridian (e.g., \'93N. 40\'b0 E.,\'94 \'93N. 80\'b0 E.\'94).  \
\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\sl324\slmult1\pardirnatural\partightenfactor0

\f0\b \cf2 Decision:
\f1\b0  For all computations and map work tied to this plaintext, treat 
\f0\b \'93EAST NORTHEAST\'94 = NORTHEAST (NE) = 45\'b0 magnetic
\f1\b0 , then apply the team\'92s declination as required.}