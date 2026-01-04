# Usage example:
#   ./eps_to_pdf "tmp/*"
for a in $1
do
  ps2pdf -r5000 $a;
done

# Usage example:
#   ./eps_optimize "tmp/*"
for a in $1
do
  inkscape --pdf-font-strategy=draw-all --export-dpi=5000 --export-text-to-path --export-type=eps --pdf-poppler $a;
done
