import unicodedata

def get_ascii(s):
    try:
        # if this works, the string only contains ascii characters
        return s.decode("ascii")
    except:
        pass

    try:
        # if possible, remove accents and print in base form
        return unicodedata.normalize("NFKD", s).encode("ascii", "ignore")
    except:
        return "--COULD NOT ASCII ENCODE--"
