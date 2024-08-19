# Install project dependencies from requirements.txt
install-deps:
	pip install -r requirements.txt

# Install development dependencies from requirements-dev.txt
install-deps-dev:
	pip install -r requirements-dev.txt

# Sort dependencies for both requirements.txt and requirements-dev.txt
sort-deps:
	sort requirements.txt -o requirements.txt
	sort requirements-dev.txt -o requirements-dev.txt

# Run the FastAPI app using uvicorn with auto-reload
dev:
	export PYTHONPATH=`pwd`/src && uvicorn inteliver.main:app --reload

# Run the service using the cli command inteliver
run:
	inteliver run

# Run mypy for type checking, Run ruff for linting
lint:
	mypy src/inteliver
	ruff check src/inteliver

# Generate HTML documentation using pdoc
docz:
	pdoc -f --html --output-dir pdoc --skip-errors --config show_source_code=False src/inteliver/

# Generate code statistics using pygount
summary:
	pygount --suffix=py  --format=summary .

# Build Docker image with the project name specified
docker-build:
	docker build -t inteliver:latest .

# Run Docker container, mapping port 8000 from container to host
docker-run:
	docker run --rm -ti -p 8000:8000 inteliver:latest

# Run semantic-release for versioning without VCS release
version:
	semantic-release version --no-vcs-release

# Run semantic-release in dry-run mode to print the next version
next-version:
	semantic-release --noop version --print

# Build distribution packages using build module
package-build:
	python -m build

# Source distribution. A “source distribution” is unbuilt (i.e. it’s not a Built Distribution), 
# and requires a build step when installed by pip.
build-sdist:
	python -m build --sdist

# Wheels. A wheel is a built package that can be installed without needing to go through the 
# “build” process.
build-wheel:
	python -m build --wheel

# Clean up generated artifacts and build files
clean:
	rm -rf dist/ build/
	$(MAKE) uninstall

# Install this project as a pypi package
install:
	pip install . --upgrade

uninstall:
	pip uninstall inteliver -y

# Run tests and write the coverage in html format
testz:
	export PYTHONPATH=`pwd`/src && pytest --disable-warnings --cov=inteliver --cov-report html tests/

# After adding new messages in the code that needs to be localized using _('new message')
# run the following:
# make translate-extract (to extract new messages in messages.pot file)
# make translate-update (to update .po files)
# Translate new messages in each language
# make translate-compile (to compile to .mo files)

# Extract translatable strings from source files and generate a .pot (Portable Object Template) file
translate-extract:
	pybabel extract -o src/inteliver/translations/messages.pot .

# create translation files for each language you want to support
translate-create:
	pybabel init -i src/inteliver/translations/messages.pot -d src/inteliver/translations -l en
	pybabel init -i src/inteliver/translations/messages.pot -d src/inteliver/translations -l fa

# compiles .po message catalogs to compiled .mo files for all langs
translate-compile:
	pybabel compile -d src/inteliver/translations

# update messages catalogs for all langs
translate-update:
	pybabel update -i src/inteliver/translations/messages.pot -d src/inteliver/translations

revision:
	alembic revision --autogenerate -m "alembic revision"

# Migrate database to the latest alembic migration
migrate:
	alembic upgrade head

# TODO: add make lint
all:      
	$(MAKE) clean
	$(MAKE) summary
	$(MAKE) translate-compile
	$(MAKE) install
	$(MAKE) testz
	$(MAKE) package-build
