# ERRANT+ (forked from ERRANT v2.3.0)

This repository is modified to fit with the conversational grammar error correction dataset. Two features are added.

## Granularity

In the paper, we defined the importance of edits according to their importance.

- 1: Trivial: punctuations (except apostrophe), casing
- 2: Moderate: informal words (abbreviations), apostrophe for contraction
- 3: Major: grammatically incorrect

ERRANT+ can automatically label the importance level of edits, except that informal scenario in level 2 cannot be recognized because of its complexity.

## Rules of Equivalent Class

Users can also define a class of words that can be considered equivalent. For example, "it's" and "it is" are the same, therefore it should be considered equivalent to be edited to either of these two.

The equivalent rules should be provided in a .json file consisting a list of lists, where each list represents an equivalent class. 

Example:

```json
[
  ["it's", "it is"],
  ["'s", "is"]
]
```

# Original README

# ERRANT v2.3.0

This repository contains the grammatical ERRor ANnotation Toolkit (ERRANT) described in:

> Christopher Bryant, Mariano Felice, and Ted Briscoe. 2017. [**Automatic annotation and evaluation of error types for grammatical error correction**](https://www.aclweb.org/anthology/P17-1074/). In Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers). Vancouver, Canada.

> Mariano Felice, Christopher Bryant, and Ted Briscoe. 2016. [**Automatic extraction of learner errors in ESL sentences using linguistically enhanced alignments**](https://www.aclweb.org/anthology/C16-1079/). In Proceedings of COLING 2016, the 26th International Conference on Computational Linguistics: Technical Papers. Osaka, Japan.

If you make use of this code, please cite the above papers. More information about ERRANT can be found [here](https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-938.html). In particular, see Chapter 5 for definitions of error types.

# Overview

The main aim of ERRANT is to automatically annotate parallel English sentences with error type information. Specifically, given an original and corrected sentence pair, ERRANT will extract the edits that transform the former to the latter and classify them according to a rule-based error type framework. This can be used to standardise parallel datasets or facilitate detailed error type evaluation. Annotated output files are in M2 format and an evaluation script is provided.

### Example:  
**Original**: This are gramamtical sentence .  
**Corrected**: This is a grammatical sentence .  
**Output M2**:  
S This are gramamtical sentence .  
A 1 2|||R:VERB:SVA|||is|||REQUIRED|||-NONE-|||0  
A 2 2|||M:DET|||a|||REQUIRED|||-NONE-|||0  
A 2 3|||R:SPELL|||grammatical|||REQUIRED|||-NONE-|||0  
A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||1

In M2 format, a line preceded by S denotes an original sentence while a line preceded by A indicates an edit annotation. Each edit line consists of the start and end token offset of the edit, the error type, and the tokenized correction string. The next two fields are included for historical reasons (see the CoNLL-2014 shared task) while the last field is the annotator id.

A "noop" edit is a special kind of edit that explicitly indicates an annotator/system made no changes to the original sentence. If there is only one annotator, noop edits are optional, otherwise a noop edit should be included whenever at least 1 out of n annotators considered the original sentence to be correct. This is something to be aware of when combining individual M2 files, as missing noops can affect evaluation. 

# Installation

## Pip Install

The easiest way to install ERRANT and its dependencies is using `pip`. We also recommend installing it in a clean virtual environment (e.g. with `venv`). ERRANT only supports Python >= 3.3.
```
python3 -m venv errant_env
source errant_env/bin/activate
pip3 install -U pip setuptools wheel
pip3 install errant
python3 -m spacy download en
```
This will create and activate a new python3 environment called `errant_env` in the current directory. `pip` will then update some setup tools and install ERRANT, [spaCy](https://spacy.io/), [python-Levenshtein](https://pypi.org/project/python-Levenshtein/) and spaCy's default English model in this environment. You can deactivate the environment at any time by running `deactivate`, but must remember to activate it again whenever you want to use ERRANT.  

#### ERRANT and spaCy

ERRANT was originally designed to work with spaCy v1.9.0 and works best with this version. SpaCy v1.9.0 does not work with Python >= 3.7 however, and so we were forced to update ERRANT to be compatible with spaCy 2. Since spaCy 2 uses a neural system to trade speed for accuracy, this means ERRANT v2.2 is **~4x slower** than ERRANT v2.1. We have not yet extended ERRANT to work with spaCy 3, but preliminary tests suggest ERRANT will become even slower. 

Consequently, we recommend ERRANT v2.1.0 if speed is a priority and you can use Python < 3.7.  
```
pip3 install errant==2.1.0
```

#### BEA-2019 Shared Task

ERRANT v2.0.0 was designed to be fully compatible with the [BEA-2019 Shared Task](https://www.cl.cam.ac.uk/research/nl/bea2019st/). If you want to directly compare against the results in the shared task, you should make sure to install ERRANT v2.0.0 as newer versions may produce slightly different scores. You can also use [Codalab](https://competitions.codalab.org/competitions/20228) to evaluate anonymously on the shared task datasets. ERRANT v2.0.0 is not compatible with Python >= 3.7.  
```
pip3 install errant==2.0.0
```

## Source Install

If you prefer to install ERRANT from source, you can instead run the following commands:
```
git clone https://github.com/chrisjbryant/errant.git
cd errant
python3 -m venv errant_env
source errant_env/bin/activate
pip3 install -U pip setuptools wheel
pip3 install -e .
python3 -m spacy download en
```
This will clone the github ERRANT source into the current directory, build and activate a python environment inside it, and then install ERRANT and all its dependencies. If you wish to modify ERRANT code, this is the recommended way to install it.

# Usage

## CLI

Three main commands are provided with ERRANT: `errant_parallel`, `errant_m2` and `errant_compare`. You can run them from anywhere on the command line without having to invoke a specific python script.  

1. `errant_parallel`  

     This is the main annotation command that takes an original text file and at least one parallel corrected text file as input, and outputs an annotated M2 file. By default, it is assumed that the original and corrected text files are word tokenised with one sentence per line.  
	 Example:
	 ```
	 errant_parallel -orig <orig_file> -cor <cor_file1> [<cor_file2> ...] -out <out_m2>
	 ```

2. `errant_m2`  

     This is a variant of `errant_parallel` that operates on an M2 file instead of parallel text files. This makes it easier to reprocess existing M2 files. You must also specify whether you want to use gold or auto edits; i.e. `-gold` will only classify the existing edits, while `-auto` will extract and classify automatic edits. In both settings, uncorrected edits and noops are preserved.  
     Example:
	 ```
	 errant_m2 {-auto|-gold} m2_file -out <out_m2>
	 ```

3. `errant_compare`  

     This is the evaluation command that compares a hypothesis M2 file against a reference M2 file. The default behaviour evaluates the hypothesis overall in terms of span-based correction. The `-cat {1,2,3}` flag can be used to evaluate error types at increasing levels of granularity, while the `-ds` or `-dt` flag can be used to evaluate in terms of span-based or token-based detection (i.e. ignoring the correction). All scores are presented in terms of Precision, Recall and F-score (default: F0.5), and counts for True Positives (TP), False Positives (FP) and False Negatives (FN) are also shown.  
	 Examples:
	 ```
     errant_compare -hyp <hyp_m2> -ref <ref_m2> 
     errant_compare -hyp <hyp_m2> -ref <ref_m2> -cat {1,2,3}
     errant_compare -hyp <hyp_m2> -ref <ref_m2> -ds
     errant_compare -hyp <hyp_m2> -ref <ref_m2> -ds -cat {1,2,3}
	 ```	

All these scripts also have additional advanced command line options which can be displayed using the `-h` flag. 

## API

As of v2.0.0, ERRANT now also comes with an API.

### Quick Start

```
import errant

annotator = errant.load('en')
orig = annotator.parse('This are gramamtical sentence .')
cor = annotator.parse('This is a grammatical sentence .')
edits = annotator.annotate(orig, cor)
for e in edits:
    print(e.o_start, e.o_end, e.o_str, e.c_start, e.c_end, e.c_str, e.type)
```

### Loading

`errant`.**load**(lang, nlp=None)  
Create an ERRANT Annotator object. The `lang` parameter currently only accepts `'en'` for English, but we hope to extend it for other languages in the future. The optional `nlp` parameter can be used if you have already preloaded spacy and do not want ERRANT to load it again.

```
import errant
import spacy

nlp = spacy.load('en')
annotator = errant.load('en', nlp)
```

### Annotator Objects

An Annotator object is the main interface for ERRANT.

#### Methods

`annotator`.**parse**(string, tokenise=False)  
Lemmatise, POS tag, and parse a text string with spacy. Set `tokenise` to True to also word tokenise with spacy. Returns a spacy Doc object.

`annotator`.**align**(orig, cor, lev=False)  
Align spacy-parsed original and corrected text. The default uses a linguistically-enhanced Damerau-Levenshtein alignment, but the `lev` flag can be used for a standard Levenshtein alignment. Returns an Alignment object.

`annotator`.**merge**(alignment, merging='rules')  
Extract edits from the optimum alignment in an Alignment object. Four different merging strategies are available:
1. rules: Use a rule-based merging strategy (default)
2. all-split: Merge nothing: MSSDI -> M, S, S, D, I
3. all-merge: Merge adjacent non-matches: MSSDI -> M, SSDI
4. all-equal: Merge adjacent same-type non-matches: MSSDI -> M, SS, D, I

Returns a list of Edit objects.

`annotator`.**classify**(edit)  
Classify an edit. Sets the `edit.type` attribute in an Edit object and returns the same Edit object. 

`annotator`.**annotate**(orig, cor, lev=False, merging='rules')  
Run the full annotation pipeline to align two sequences and extract and classify the edits. Equivalent to running `annotator.align`, `annotator.merge` and `annotator.classify` in sequence. Returns a list of Edit objects.

```
import errant

annotator = errant.load('en')
orig = annotator.parse('This are gramamtical sentence .')
cor = annotator.parse('This is a grammatical sentence .')
alignment = annotator.align(orig, cor)
edits = annotator.merge(alignment)
for e in edits:
    e = annotator.classify(e)
```

`annotator`.**import_edit**(orig, cor, edit, min=True, old_cat=False)  
Load an Edit object from a list. `orig` and `cor` must be spacy-parsed Doc objects and the edit must be of the form: `[o_start, o_end, c_start, c_end(, type)]`. The values must be integers that correspond to the token start and end offsets in the original and corrected Doc objects. The `type` value is an optional string that denotes the error type of the edit (if known). Set `min` to True to minimise the edit (e.g. [a b -> a c] = [b -> c]) and `old_cat` to True to preserve the old error type category (i.e. turn off the classifier).

```
import errant

annotator = errant.load('en')
orig = annotator.parse('This are gramamtical sentence .')
cor = annotator.parse('This is a grammatical sentence .')
edit = [1, 2, 1, 2, 'SVA'] # are -> is
edit = annotator.import_edit(orig, cor, edit)
print(edit.to_m2())
```

### Alignment Objects

An Alignment object is created from two spacy-parsed text sequences.

#### Attributes

`alignment`.**orig**  
`alignment`.**cor**  
The spacy-parsed original and corrected text sequences.

`alignment`.**cost_matrix**   
`alignment`.**op_matrix**  
The cost matrix and operation matrix produced by the alignment.

`alignment`.**align_seq**  
The first cheapest alignment between the two sequences.

### Edit Objects

An Edit object represents a transformation between two text sequences.

#### Attributes

`edit`.**o_start**  
`edit`.**o_end**  
`edit`.**o_toks**  
`edit`.**o_str**  
The start and end offsets, the spacy tokens, and the string for the edit in the *original* text.

`edit`.**c_start**  
`edit`.**c_end**  
`edit`.**c_toks**  
`edit`.**c_str**  
The start and end offsets, the spacy tokens, and the string for the edit in the *corrected* text.

`edit`.**type**  
The error type string.

#### Methods

`edit`.**to_m2**(id=0)  
Format the edit for an output M2 file. `id` is the annotator id.	

## Development for Other Languages

If you want to develop ERRANT for other languages, you should mimic the `errant/en` directory structure. For example, ERRANT for French should import a merger from `errant.fr.merger` and a classifier from `errant.fr.classifier` that respectively have equivalent `get_rule_edits` and `classify` methods. You will also need to add `'fr'` to the list of supported languages in `errant/__init__.py`.

# Contact

If you have any questions, suggestions or bug reports, you can contact the authors at:  
christopher d0t bryant at cl.cam.ac.uk  
mariano d0t felice at cl.cam.ac.uk  