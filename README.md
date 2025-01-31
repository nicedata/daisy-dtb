# A package to deal with Daisy 2.02 digital talking books

## Introduction

DAISY (Digital Accessible Information SYstem) is a technical standard for digital audio books, periodicals and computerized text. 

DAISY is designed to be a complete audio substitute for print material and is specifically designed for use by people with "print disabilities", including blindness, impaired vision, and dyslexia. Based on the MP3 and XML formats, the DAISY format has advanced features in addition to those of a traditional audio book. Users can search, place bookmarks, precisely navigate line by line, and regulate the speaking speed without distortion. DAISY also provides aurally accessible tables, references and additional information. 

As a result, DAISY allows visually impaired listeners to navigate something as complex as an encyclopedia or textbook, otherwise impossible using conventional audio recordings. 

DAISY multimedia can be a book, magazine, newspaper, journal, computerized text or a synchronized presentation of text and audio. It provides up to six embedded "navigation levels" for content, including embedded objects such as images, graphics, and MathML. In the DAISY standard, navigation is enabled within a sequential and hierarchical structure consisting of (marked-up) text synchronized with audio. 

DAISY 2 was based on XHTML and SMIL. DAISY 3 is a newer technology, also based on XML, and is standardized as ANSI/NISO Z39.86-2005. 

The DAISY Consortium was founded in 1996 and consists of international organizations committed to developing equitable access to information for people who have a print disability. The consortium was selected by the National Information Standards Organization (NISO) as the official maintenance agency for the DAISY/NISO Standard.

Source : https://encyclopedia.pub/entry/33638

## Warning

**This package (also published to PyPi) is still under active development (alpha stage).**

## Installation

You can install `daisy-dtb` with all common python dependancies manager.

* With pip : ```pip install daisy-dtb```
* With uv : ```uv add daisy-dtb```

## DTB data sources

A Daisy 2.02 digital talking book (DTB) can be available in multiple forms :

- in a file system folder or in a web location as individual files
- in a ZIP archive located in a file system folder or on a website

The base class representing this is `DtbResource` (an abstract class inheriting from `ABC`).
A data source must contain a Daisy 2.02 book.

Two kinds of `DtbResource` classes have been implemented :

- `FolderDtbResource` : the resource base is a filesystem folder or a web location containing the DTB files
- `ZipDtbResource` : the resource base is a zip file (either on a filesystem or in a web location) containing the DTB files

Both classes implement the `get(resource_name: str) -> bytes | str | None` method which allows to retrieve a specific resource (e.g. the ncc.html file). 
The conversion to a `str` type result is tried, and if it does not work, `bytes` are returned. In cas of an error, `None` is returned.

The imlementation can be found in the `dtbsource.py` file.

These classes are used to specifiy the `source` of a `DaisyDTB`, the class representing the Daisy 2.02 book.

<u>Note 1</u> : If `ZipDtbResource` is instaciated from a web location, data is stored internally to avoid multiple accesses to the web.

<u>Note 2</u> : If `FolderDtbResource` is instaciated, a `buffer_size` can be set. This allows to store resources internally to reduce network traffic.

### Setting up a datasource

For Daisy books stored in a filesystem :

```python
try:
    # Create a `FolderDtbResource` with a `buffer_size` of 10 items
    source = FolderDtbResource(resource_base='/path/to/a/dtb/folder/', buffer_size=10)
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
    # Create a `FolderDtbResource` with a `buffer_size` of 20 items
    source = FolderDtbResource(resource_base='https://www.site.com/daisy/book/', buffer_size=20)
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