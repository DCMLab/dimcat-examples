---
jupyter:
  jupytext:
    formats: py:percent,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.14.4
  kernelspec:
    display_name: dimcat
    language: python
    name: dimcat
---

# Working with Harmonic Annotations

```python
import dimcat as dc
import pandas as pd
```

## Load dataset

Use dimcat's `Dataset` class to load a dataset.
Each dataset consists of several subcorpora (here only `ABC`),
which in turn consist of several pieces (here `n01_op18-1_01`, `n01_op18-1_02`, etc.).

A `Dataset` has several representations of each piece (e.g. a list of chord labels or a list of notes) called *facets*.
Each facet is represented by a dataframe.

Corpora can be processed, e.g. slicing notes according to different criteria (see below).
The output of these operations is again a dataset with facets.

```python
# this takes some time because it parses the original data, not the preprocessed tsv files
dataset = dc.Dataset()
dataset.load("./ABC", parse_tsv=False, parse_scores=True) # make sure to parse directly from MuseScore files
dataset.data
```

## Get chord labels

Chord labels are stored in the `expanded` facet.
Using `.get_facet()` returns a single dataframe with all chord labels.
Corpus, piece, and timespan ("interval") are encoded in an hierarchical index.

```python
labels = dataset.get_facet("expanded")
labels
```

## Get salami slices

Use the `NoteSlicer` to obtain a sliced version of the dataset.
Querying the note facet returns the sliced notes.

```python
# this takes some time
salami_dts = dc.NoteSlicer().process_data(dataset)
salami_notes = salami_dts.get_facet("notes")
salami_notes
```

# Match salami slices with chord labels

Each chord label has an `interval` index that encodes its timespan.
We can use this to find the corresponding slices from the previous step.

Let's try this for a single chord. Start by getting the interval of the first chord in the first piece:

```python
# zoom in on the chords in one piece
chords = labels.loc[('ABC', 'n01op18-1_01')]
chords
```

```python
# get the interval of the first chord...
chord0_interval = chords.index[0]
chord0_interval # this is a pandas Interval
```

```python
# and the chord itself
chord0 = chords.loc[chord0_interval]
chord0
```

Finally, find all slices in the same piece that overlap with the chord:

```python
salamis = salami_notes.loc[("ABC", "n01op18-1_01")]
salamis[salamis.index.get_level_values(0).overlaps(chord0_interval)]
```

## Rest...

```python
salami_notes.loc[("ABC", "n01op18-1_01")]
```

```python
salami_notes.loc[("ABC", "n01op18-1_01", pd.Interval(12.0,13.0,closed='left'))]
```

```python
str(pd.Interval(0.0,1.0,closed='left'))
```

```python
salami_dts.get_slice_info()
```
