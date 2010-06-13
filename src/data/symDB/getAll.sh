#!/bin/bash

wget -O .tmp http://www.cryst.ehu.es/cgi-bin/cryst/programs/nph-getgen 2> /dev/null
awk 'BEGIN{ RS="\""}($0~/cgi-bin/){ print $0 }' .tmp > .allLinks
rm .tmp

sed -i '{s/&/\\&/g;s/?/\\?/g;s/=/\\=/g;s/^/http:\/\/www.cryst.ehu.es/}' .allLinks

cat /dev/null > .ids
for val in `cat .allLinks`
do
	id=`echo $val | awk 'BEGIN{RS="[\&]+"}($1~/gnum/){print $1}' | awk 'BEGIN{FS="="}{print $2}' | sed '{s/\\\//g}'`
	echo "wget -O $id.htmlTmp" >> .ids
done

paste .ids .allLinks > .output
rm .ids .allLinks

chmod +x .output
./.output
rm .output

for val in `ls *.htmlTmp`
do
	awk 'BEGIN{RS="[<>]"}{print $0}' $val | grep -A3 "^pre" | sed '{s/pre//g;/--/d}' > ${val%.htmlTmp}.sym
	rm $val
done
