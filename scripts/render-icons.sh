#!/usr/bin/env bash
# Rasterise the app mark into the PWA icon set under static/icons/.
#
# Sibling of render-og.sh, and deliberately NOT wired into `pnpm build`:
# .vercelignore excludes scripts/, so a build that ran this would die on the
# deploy host with a missing-file error. The outputs are committed instead —
# same arrangement as check-kits.py. Re-run after editing the mark.
#
# Two shapes come out of one source:
#
#   icon-<n>.png     the mark as drawn, edge to edge. What a browser shows when
#                    it does not mask.
#   maskable-512.png the same mark inset to 80% on a full-bleed gold field.
#                    Android crops a maskable icon to whatever shape the
#                    launcher uses (circle, squircle, teardrop), and the crop
#                    can take ~10% off each edge. The mark's own rounded tile
#                    would get its corners shaved and read as a mistake, so the
#                    maskable variant gives the crop its own margin to eat.
set -euo pipefail

cd "$(dirname "$0")/.."

SRC=src/lib/assets/favicon.svg
OUT=static/icons
mkdir -p "$OUT"

# Any of the three; whichever this machine has. Chrome is last because it is the
# slowest and needs a page wrapped round the SVG.
render() { # render <svg> <px> <out>
	local svg=$1 px=$2 out=$3
	if command -v rsvg-convert >/dev/null; then
		rsvg-convert -w "$px" -h "$px" -o "$out" "$svg"
	elif command -v inkscape >/dev/null; then
		inkscape "$svg" -w "$px" -h "$px" -o "$out" >/dev/null 2>&1
	elif command -v magick >/dev/null; then
		magick -background none "$svg" -resize "${px}x${px}" "$out"
	else
		echo "need one of rsvg-convert, inkscape or magick" >&2
		exit 1
	fi
	[ -s "$out" ] || { echo "produced nothing: $out" >&2; exit 1; }
}

for px in 192 512; do
	render "$SRC" "$px" "$OUT/icon-$px.png"
	echo "icon-$px.png"
done

# The maskable variant: same drawing at 80%, centred on the gold the mark's own
# tile already uses, so the safe-zone padding is invisible rather than a border.
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
{
	printf '<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">'
	printf '<rect width="512" height="512" fill="#f0c040"/>'
	printf '<g transform="translate(51.2 51.2) scale(0.8)">'
	# Inline the mark minus its own <svg> wrapper and its rounded tile — the
	# field above is already gold, and the tile's corners are what the crop eats.
	sed -e '1d' -e '$d' "$SRC" \
		| grep -v '<rect' \
		| grep -v '<title>' \
		| grep -v '^\s*<!--' \
		| grep -v '^\s*[a-z].*-->'
	printf '</g></svg>'
} > "$tmp/maskable.svg"

render "$tmp/maskable.svg" 512 "$OUT/maskable-512.png"
echo "maskable-512.png"

ls -l "$OUT"
