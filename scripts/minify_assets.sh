#!/usr/bin/env bash
# One-off maintenance script: regenerate the minified CSS/JS the templates
# actually serve. Re-run this after editing any of the source files below,
# then commit both the source and the regenerated .min files together - this
# does not run automatically as part of any build or deploy step.
#
# Uses terser for JS (safe, real-parser based) and lightningcss for CSS.
# clean-css-cli was tried first and rejected: it doesn't understand the
# native CSS nesting used in landing.css and silently drops nested rules
# (e.g. the .header-wrapper:hover { .header { ... } } block) instead of
# erroring - lightningcss handles it correctly.
#
# Usage: bash scripts/minify_assets.sh

set -euo pipefail
cd "$(dirname "$0")/.."

npx --yes terser static/js/static.js -c -m -o static/js/static.min.js
npx --yes terser static/js/carousel.js -c -m -o static/js/carousel.min.js

npx --yes lightningcss-cli --minify static/css/style.css -o static/css/style.min.css
npx --yes lightningcss-cli --minify static/css/landing.css -o static/css/landing.min.css

echo "Done. Diff the .min files and commit alongside the source changes that prompted this run."
