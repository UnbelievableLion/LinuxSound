#!/bin/bash

# Update table of contents, perface and sections
# only update .md files that have changed
# git add changed files, but do not commit

# ensure SUMMARY.md is current
python get_content.py SUMMARY.md.new
if ! cmp SUMMARY.md SUMMARY.md.new
then
    mv SUMMARY.md.new SUMMARY.md
    git add SUMMARY.md
else
    rm SUMMARY.md.new
fi

# ensure all README.md are up to date
python get_preface.py .new
for f in */*/README.md
do
    # some .md files are created by other programs
    # Ignore these
    test -f "$f.new" || continue

    if ! cmp "$f" "$f.new"
    then
	mv "$f.new" "$f"
	git add "$f"
    else
	rm "$f.new"
    fi
done

# ensure all sections are up to date
python get_dom_sections.py .new
for f in */*/*.md
do
    # some .md files are created by e.g. get_preface
    # not by get_dom_sections. ignore these
    test -f "$f.new" || continue

    if ! cmp "$f" "$f.new"
    then
	mv "$f.new" "$f"
	git add "$f"
    else
	rm "$f.new"
    fi
done
