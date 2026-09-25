#!/bin/sh
# Build python3-styledscriptures_<version>_all.deb and styledscriptures-data_<version>_all.deb.
# Usage: packaging/deb/build.sh
set -eu

cd "$(dirname "$0")/../.."
REPO_ROOT="$(pwd)"
VERSION="0.$(git rev-list --count HEAD)"
sed -i "s/^Version: .*/Version: $VERSION/" packaging/deb/control-styledscriptures
sed -i "s/^Version: .*/Version: $VERSION/" packaging/deb/control-styledscriptures-data
sed -i "s/^Version: .*/Version: $VERSION/" packaging/deb/control-styledscriptures-web
sed -i "s/^version = .*/version = \"$VERSION\"/" pyproject.toml

# --- python3-styledscriptures (code) ---
CODE_DIR="$REPO_ROOT/debian-pkg-styledscriptures"
rm -rf "$CODE_DIR"
mkdir -p "$CODE_DIR/DEBIAN" "$CODE_DIR/usr/lib/python3/dist-packages" \
	"$CODE_DIR/usr/share/doc/python3-styledscriptures"
cp packaging/deb/control-styledscriptures "$CODE_DIR/DEBIAN/control"
cp Text.py Psalms.py Parashot.py "$CODE_DIR/usr/lib/python3/dist-packages/"
cp GPL-3 "$CODE_DIR/usr/share/doc/python3-styledscriptures/copyright"
dpkg-deb --build --root-owner-group "$CODE_DIR" "python3-styledscriptures_${VERSION}_all.deb"
rm -rf "$CODE_DIR"
echo "Built python3-styledscriptures_${VERSION}_all.deb"

# --- styledscriptures-data (static reference data + editable text/metadata) ---
DATA_DIR="$REPO_ROOT/debian-pkg-styledscriptures-data"
rm -rf "$DATA_DIR"
mkdir -p "$DATA_DIR/DEBIAN" "$DATA_DIR/usr/share/styledscriptures/csv" \
	"$DATA_DIR/var/lib/styledscriptures/csv" \
	"$DATA_DIR/var/lib/styledscriptures/psalms" "$DATA_DIR/var/lib/styledscriptures/parashot"
cp packaging/deb/control-styledscriptures-data "$DATA_DIR/DEBIAN/control"
cp parashot.csv "$DATA_DIR/usr/share/styledscriptures/csv/"
cp episodes.csv "$DATA_DIR/var/lib/styledscriptures/csv/"
cp parashot.md psalms.md "$DATA_DIR/var/lib/styledscriptures/"
cp text/psalms/*.md "$DATA_DIR/var/lib/styledscriptures/psalms/"
cp text/parashot/*.md "$DATA_DIR/var/lib/styledscriptures/parashot/"
dpkg-deb --build --root-owner-group "$DATA_DIR" "styledscriptures-data_${VERSION}_all.deb"
rm -rf "$DATA_DIR"
echo "Built styledscriptures-data_${VERSION}_all.deb"

# --- styledscriptures-web (Flask app) ---
WEB_DIR="$REPO_ROOT/debian-pkg-styledscriptures-web"
rm -rf "$WEB_DIR"
mkdir -p "$WEB_DIR/DEBIAN" "$WEB_DIR/usr/share/styledscriptures" "$WEB_DIR/usr/bin" \
	"$WEB_DIR/usr/share/doc/styledscriptures-web"
cp packaging/deb/control-styledscriptures-web "$WEB_DIR/DEBIAN/control"
cp styledscriptures-web.py "$WEB_DIR/usr/share/styledscriptures/styledscriptures-web.py"
chmod +x "$WEB_DIR/usr/share/styledscriptures/styledscriptures-web.py"
ln -s ../share/styledscriptures/styledscriptures-web.py "$WEB_DIR/usr/bin/styledscriptures-web"
cp GPL-3 "$WEB_DIR/usr/share/doc/styledscriptures-web/copyright"
dpkg-deb --build --root-owner-group "$WEB_DIR" "styledscriptures-web_${VERSION}_all.deb"
rm -rf "$WEB_DIR"
echo "Built styledscriptures-web_${VERSION}_all.deb"
