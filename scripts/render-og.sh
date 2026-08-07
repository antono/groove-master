#!/usr/bin/env bash
# Rasterise docs/og-card.svg into static/og.png, the 1200x630 social preview.
#
# Headless Chrome rather than qlmanage (which made static/logo.png and the
# favicons): QuickLook only produces square thumbnails, and it renders a
# landscape SVG oversized and then crops it. Chrome honours --window-size
# exactly, and resolves the same system-ui font stack the site itself uses.
set -euo pipefail

cd "$(dirname "$0")/.."

CHROME=${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}
[ -x "$CHROME" ] || { echo "no Chrome at $CHROME — set CHROME=/path/to/chrome" >&2; exit 1; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

# The SVG needs a page around it: Chrome's default body margin would otherwise
# push the card 8px down and right, losing a strip off the bottom edge.
{
	printf '<!doctype html><meta charset="utf-8"><style>html,body{margin:0;padding:0;overflow:hidden}</style>'
	cat docs/og-card.svg
} > "$tmp/card.html"

"$CHROME" --headless --disable-gpu --hide-scrollbars \
	--force-device-scale-factor=1 --window-size=1200,630 \
	--screenshot="$tmp/og.png" "$tmp/card.html" >/dev/null 2>&1

[ -s "$tmp/og.png" ] || { echo "Chrome produced nothing — is docs/og-card.svg valid XML?" >&2; exit 1; }
mv "$tmp/og.png" static/og.png

sips -g pixelWidth -g pixelHeight static/og.png
