tag:
	git tag -a v${VERSION} -m "release version ${VERSION}"
	git push origin v${VERSION}

tree:
	tree -L 2 -a --dirsfirst -I '.DS_Store|__pycache__|.archive/|.git|.ruff_cache|.venv|.gitkeep'
