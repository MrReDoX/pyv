for a in ./23_09_2023/*
do
  inkscape --pdf-font-strategy=draw-all --export-dpi=5000 --export-text-to-path --export-type=eps --pdf-poppler $a;
done
