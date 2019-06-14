#!/bin/sh

F=$(mktemp punchXXXXX.cob)
cat > $F
cobc -x $F
./`basename $F .cob`
rm `basename $F .cob`
rm $F
