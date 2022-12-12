# ---
# jupyter:
#   jupytext:
#     formats: py:percent,md
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: dimcat
#     language: python
#     name: dimcat
# ---

# %% [markdown]
# # Working with Harmonic Annotations

# %%
import dimcat as dc
import pandas as pd

# %% [markdown]
# ## Load corpus
#
# Use dimcat's `Corpus` class to load a dataset.
# Each corpus consists of several subcorpora (here only `ABC`),
# which in turn consist of several pieces (here `n01_op18-1_01`, `n01_op18-1_02`, etc.).
#
# A `Corpus` has several representations of each piece (e.g. a list of chord labels or a list of notes) called *facets*.
# Each facet is represented by a dataframe.
#
# Corpora can be processed, e.g. slicing notes according to different criteria (see below).
# The output of these operations is again a corpus with facets.

# %%
# this takes some time because it parses the original data, not the preprocessed tsv files
corpus = dc.Corpus()
corpus.load("./ABC", parse_tsv=False, parse_scores=True) # make sure to parse directly from MuseScore files
corpus.data

# %% [markdown]
# ## Get chord labels
#
# Chord labels are stored in the `expanded` facet.
# Using `.get_facet()` returns a single dataframe with all chord labels.
# Subcorpus, piece, and timespan ("interval") are encoded in an hierarchical index.

# %%
labels = corpus.get_facet("expanded")
labels

# %% [markdown]
# ## Get salami slices
#
# Use the `NoteSlicer` to obtain a sliced version of the corpus.
# Querying the note facet returns the sliced notes.

# %%
# this takes some time
salami_crp = dc.NoteSlicer().process_data(corpus)
salami_notes = salami_crp.get_facet("notes")
salami_notes

# %% [markdown]
# # Match salami slices with chord labels
#
# Each chord label has an `interval` index that encodes its timespan.
# We can use this to find the corresponding slices from the previous step.
#
# Let's try this for a single chord. Start by getting the interval of the first chord in the first piece:

# %%
# zoom in on the chords in one piece
chords = labels.loc[('ABC', 'n01op18-1_01')]
chords

# %%
# get the interval of the first chord...
chord0_interval = chords.index[0]
chord0_interval # this is a pandas Interval

# %%
# and the chord itself
chord0 = chords.loc[chord0_interval]
chord0

# %% [markdown]
# Finally, find all slices in the same piece that overlap with the chord:

# %%
salamis = salami_notes.loc[("ABC", "n01op18-1_01")]
salamis[salamis.index.get_level_values(0).overlaps(chord0_interval)]

# %% [markdown]
# ## Rest...

# %%
salami_notes.loc[("ABC", "n01op18-1_01")]

# %%
salami_notes.loc[("ABC", "n01op18-1_01", pd.Interval(12.0,13.0,closed='left'))]

# %%
str(pd.Interval(0.0,1.0,closed='left'))

# %%
salami.get_slice_info()

# %%
