# Usage example:
#   ./eps_optimize "tmp/*"
for a in $1
do
  inkscape --pdf-font-strategy=draw-all --export-dpi=5000 --export-text-to-path --export-type=eps --pdf-poppler $a;
done
