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
import pandas as pd
import pitchtypes as pt # this requires the development branch of pitchtypes
import seaborn as sns
import dimcat as dc
import logging
log = logging.getLogger()
log.setLevel(logging.WARNING)

# %% [markdown]
# ## Load dataset
#
# Use dimcat's `Dataset` class to load a dataset.
# Each dataset consists of several corpora (here only `ABC`),
# which in turn consist of several pieces (here `n01_op18-1_01`, `n01_op18-1_02`, etc.).
#
# A `Dataset` has several representations of each piece (e.g. a list of chord labels or a list of notes) called *facets*.
# Each facet is represented by a dataframe.
#
# Corpora can be processed, e.g. slicing notes according to different criteria (see below).
# The output of these operations is again a dataset with facets.

# %%
# this takes some time because it parses the original data, not the preprocessed tsv files
dataset = dc.Dataset()
dataset.load("./ABC")
dataset.data

# %% [markdown]
# ## Get notes

# %%
notes = dataset.get_facet("notes")
notes


# %% [markdown]
# ## Example 1: Get pitches from dataframe and store them back
#
# Translate pitch columns to actual pitches:

# %%
def get_pitches(tpc, midi):
    """
    Takes the tpc and midi columns of the notes df.
    Returns a SpelledPitchArray
    """
    pcs = pt.SpelledPitchClassArray(tpc)
    alterations = pcs.alteration()
    midi_base = midi - alterations
    octaves = (midi_base // 12) - 1
    return pt.SpelledPitchArray.from_independent(tpc, octaves)

pitches = get_pitches(notes['tpc'], notes['midi'])
pitches

# %% [markdown]
# Assign back into dataframe:

# %%
notes['pitch_str'] = pitches.name() # a vector of names
notes['octave'] = pitches.octaves() # this makes it easier to convert back to a pitch array
notes

# %% [markdown]
# ## Example 2: Express all pitches relative to the key of the piece
#
# We get the keys from the harmonic annotations:

# %%
labels = dataset.get_facet("expanded")
labels

# %% [markdown]
# The global key is constrant throughout a piece, so we group by piece and take the first entry in each group.

# %%
keys = labels['globalkey'].groupby(['corpus', 'fname']).first()
keys

# %%
keys[('ABC', 'n01op18-1_01')]


# %% [markdown]
# Now we group the dataframe by piece, get the key of each piece, and translate its pitches to intervals from the root (in octave 0).

# %%
def to_relative_pitch(grp):
    # find root
    index = grp.name
    root_name = keys[index]
    # the pitch's letter must be uppercase,
    # but the harmonic labels express minor keys using lowercase letters:
    root_name = root_name[0].upper() + root_name[1:]
    root = pt.SpelledPitchClass(root_name)
    
    # add new colums to the group: the key's root (name and tpc) and the relative pitch of each note
    grp = grp.copy()
    grp['global_root'] = str(root)
    grp['global_root_tpc'] = root.fifths()
    # load pitches from dataframe columns
    pitches = pt.SpelledPitchArray.from_independent(grp['tpc'], grp['octave'])
    # since the root is only a pitch class, we express pitches as interval classes.
    # alternatively, we could embed the root into pitch space (octave 0) and work with non-class intervals
    rel_pitches = pitches.pc() - root
    grp['rel_pitch'] = rel_pitches.name() # don't just assign rel_pitches, this will convert to a list of SpelledIntervalClass objects
    grp['rel_tic'] = rel_pitches.fifths()
    return grp

# group by piece and add columns
df_rel = notes.groupby(['corpus', 'fname'], axis="rows", sort=False, group_keys=False).apply(to_relative_pitch)
df_rel
df_rel[['tpc', 'midi', 'pitch_str', 'global_root', 'global_root_tpc', 'rel_pitch', 'rel_tic']]

# %% [markdown]
# Let's plot the distribution of untransposed tpcs vs the distribution of tpcs. You can see that the relative tpc is distributed more narrowly because we removed the variance that is due to the choice of key.

# %%
sns.histplot(data=df_rel[['tpc', 'rel_tic']].melt(var_name='type', value_name='fifth'),
             x='fifth',
             hue='type',
             stat='density',
             element='step',
             discrete=True)

# %%
