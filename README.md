# A library to deal with Daisy 2.02 digital talking books

## Installation

You can install `daisy-dtb` with all common python dependancies manager.

* With pip : ```pip install daisy-dtb```
* With uv : ```uv add daisy-dtb```

## Data sources

A Daisy 2.03 digital talking book (DTB) can be available in multiple forms :

- in a filesystem folder or in a web location as individual files
- in a ZIP archive located in a filesystem folder or on a website

The base class representing this is `DtbResource` (an abstract class iheriting from `ABC`).
A data source must contain a Daisy 2.02 book.

Two kinds of `DtbResource` classes have been implemented :

- `FolderDtbResource` : the resource base is a filesystem folder or a web location containing the DTB files
- `ZipDtbResource` : the resource base is a zip file (either on a filesystem or in a web location) containing the DTB files

Both classes implement the `get(resource_name: str) -> bytes | str | None` method which allows to retrieve a specific resource (e.g. the ncc.html file). 
The conversion to a `str` type result is tried, and if it does not work, `bytes` are returned. In cas of an error, `None` is returned.

The imlementation can be found in the `dtbsource.py` file.

These classes are used to specifiy the `source` of a `DaisyDTB`, the class representing the Daisy 2.02 book.

<u>Note</u> : If `ZipDtbResource` is instaciated from a web location, data is stored internally to avoid multiple accesses to the web.

### Setting up a datasource

For Daisy books stored in a filesystem :

```python
try:
    source = FolderDtbResource(resource_base='/path/to/a/dtb/folder/')
except FileNotFoundError:
    # Handle error
    ...  

data = source.get('ncc.html')
if data is not None:
    # Process the data
    ...

```

For Daisy books stored in a web location :

```python
try:
    source = FolderDtbResource(resource_base='https://www.site.com/daisy/book/')
except FileNotFoundError:
    # Handle error
    ...  

data = source.get('ncc.html')
if data is not None:
    # Process the data
    ...

```

For Daisy books stored in a local ZIP file :

```python
try:
    source = ZipDtbResource(resource_base='/path/to/a/dtb/zipfile.zip')
except FileNotFoundError:
    # Handle error
    ...  

data = source.get('ncc.html')
if data is not None:
    # Process the data
    ...

```

For Daisy books stored in a ZIP file on a web site :

```python
try:
    source = ZipDtbResource(resource_base='https://www.site.com/daisy/book/zipfile.zip')
except FileNotFoundError:
    # Handle error
    ...  

data = source.get('ncc.html')
if data is not None:
    # Process the data
    ...

```

## Project files

- `dtbsource.py` : implementation of the  `DtbResource`, `FolderDtbResource` and `ZipDtbResource` classes
- `domlib.py` : classes to encapsulate and simplify the usage of the `xml.dom.minidom` library

## Dependencies

We use the `loguru` package for logging.

See file `pyproject.toml`.





## References

* [Daisy 2.02 specifications](https://daisy.org/activities/standards/daisy/daisy-2/daisy-format-2-02-specification/)