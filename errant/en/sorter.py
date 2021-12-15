from errant.en.classifier import conts

conts_expanded = {
    "would": "'d",
    "will": "'ll",
    "am": "'m",
    "not": "n't",
    "are": "'re",
    "is": "'s",
    "has": "'s",
    "have": "'ve",
}

# Input: An Edit object
# Output: Whether the Edit adds apostrophe to a contraction token
# e.g. nt -> n't
#      its -> it 's
def add_apostr_for_cont(edit):
    # Check token number
    if len(edit.o_toks) and len(edit.c_toks):
        return edit.c_toks[-1].lower_ in conts and \
               "".join([x.lower_ for x in edit.o_toks]) == \
               "".join([x.lower_ for x in edit.c_toks]).replace("'", "")
    else:
        return False

# Input: An Edit object
# Output: Whether the Edit decomposes a contraction token without apostrophe
# e.g. its -> it is
def decomp_cont(edit):
    # Check token number
    if len(edit.c_toks) == 2 and len(edit.o_toks) == 1:
        # Find the expanded token's contraction form
        if edit.c_toks[-1].lower_ in conts_expanded:
            contraction = edit.c_toks[0].lower_ + conts_expanded[edit.c_toks[-1].lower_]
            return contraction.replace("'", "") == edit.o_toks[0].lower_
        else:
            return False
    else:
        return False

# Input: An Edit object
# Output: The same Edit object with an updated importance level
# 1: Trivial: punctuations (except apostrophe), casing
# 2: Moderate: informal words (abbreviations), apostrophe for contraction
# 3: Major: grammatically incorrect
def sort(edit):
    # Apostrophe for contraction
    # 1. nt -> n't
    # 2. its -> it is
    if add_apostr_for_cont(edit) or decomp_cont(edit):
        edit.importance = 2
    # Punctuations, casing
    elif edit.type.endswith("PUNCT") or \
            edit.type.endswith("ORTH"):
        edit.importance = 1
    # Everything left is identified as 3
    else:
        edit.importance = 3

    return edit
