# eps -> pdf
for a in ./23_09_2023/*
do
  ps2pdf -r2500 $a;
  # printf $a
done

# optimize eps
# inkscape --pdf-font-strategy=draw-all --export-dpi=5000 --export-text-to-path --export-type=eps --pdf-poppler
