# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import glob
import sys
import re
from util import basename_noext
from util import sort_by_value


class NGramModel(object):
    SPLITCHARS = re.compile(r"[][}{)( \n\t:!.?_,¶§%–\"`'·•@~\\/”«»0-9_-]")
    NB_NGRAMS = 400
    MISSING_VALUE = 400

    def __init__(self, arg={}, lang='input'):
        self.lang = lang        # for debugging

    def of_text(self, text):
        if type(text) == unicode:
            self.finish(self.freq_of_text(text, {}))
        else:
            self.finish(self.freq_of_text(text.decode('utf-8'), {}))
        return self

    def of_freq(self, freq):
        self.finish(freq)
        return self

    def of_text_file(self, f):
        self.finish(self.freq_of_text_file(f))
        return self

    def of_model_file(self, fname):
        raise NotImplementedError("You have to subclass and override of_model_file")

    def freq_of_model_file(self, fname, gram_column, freq_column):
        freq = {}
        with open(fname, 'r') as f:
            for nl, strline in enumerate(f.readlines()):
                line = strline.decode('utf-8').strip()
                if line == "":
                    continue
                parts = line.split()
                if len(parts) != 2:
                    raise ValueError("%s:%d invalid line, was split to %s"
                                     % (fname, nl+1, parts))
                try:
                    g = unicode(parts[gram_column])
                    f = int(parts[freq_column])
                    freq[g] = f
                except ValueError, e:
                    raise ValueError("%s:%d %s"%(fname,nl+1,e))
        return freq

    def tokenise(self, text):
        """Since use split() when loading the model file, we also use split()
        on the input text; this includes whitespace (like byte order
        marks) that might not all be in SPLITCHARS

        """
        tokens = ( re.split(self.SPLITCHARS, t)
                   for t in text.split() )
        return sum(tokens, [])  # flatten

    def freq_of_text(self, text, freq):
        raise NotImplementedError("You have to subclass and override freq_of_text")

    def to_model_file(self, fname):
        raise NotImplementedError("You have to subclass and override to_model_file")

    def freq_of_text_file(self, f):
        freq = {}
        for strline in f.readlines():
            freq = self.freq_of_text(strline.decode('utf-8'),
                                     freq)
        return freq

    def finish(self, freq):
        self.ngrams = {
            gram:rank
            for rank, (gram, freq)
            in enumerate(
                sort_by_value(freq, reverse=True)[:self.NB_NGRAMS]
            )
            if gram != ""
        }
        # Only store the top NB_NGRAMS with frequency:
        self.freq = {
            gram:freq[gram]
            for gram in self.ngrams
        }
        self.ngramskeyset = set(self.ngrams.keys())

    def compare(self, unknown):
        missing_count = len(unknown.ngramskeyset - self.ngramskeyset)
        d_missing = self.MISSING_VALUE * missing_count
        d_found = sum(
            abs(rank - self.ngrams[gram])
            for gram,rank
            in unknown.ngrams.iteritems() if gram in self.ngrams
        )
        return d_missing + d_found

class CharModel(NGramModel):
    def of_model_file(self, fname):
        self.finish(self.freq_of_model_file(fname, gram_column=0, freq_column=1))
        return self

    def to_model_file(self, fname):
        lines = "".join([ "%s\t%d\n" % (g, f)
                          for g, f
                          in sort_by_value(self.freq, reverse=True)
                          if g != '' ])
        with open(fname, 'w') as f:
            f.write(lines.encode('utf-8'))

    def freq_of_text(self, text, freq):
        words = self.tokenise(text)
        for word in words:
            _word_ = '_'+word+'_'
            size = len(_word_)
            for i in range(size):
                for s in (1, 2, 3, 4):
                    sub = _word_[i:i+s]
                    freq[sub] = freq.get(sub, 0) + 1
                    if i+s >= size:
                        break
        return freq


class WordModel(NGramModel):
    NB_NGRAMS = 10000
    def of_model_file(self, fname):
        self.finish(self.freq_of_model_file(fname, gram_column=1, freq_column=0))
        return self

    def to_model_file(self, fname):
        lines = "".join([ "%d\t%s\n" % (f, g)
                          for g, f
                          in sort_by_value(self.freq, reverse=True)
                          if g != '' ])
        with open(fname, 'w') as f:
            f.write(lines.encode('utf-8'))

    def freq_of_text(self, text, freq):
        words = self.tokenise(text)
        for word in words:
            freq[word] = freq.get(word, 0) + 1
        return freq

    def finish(self, freq):
        super(WordModel, self).finish(freq)
        n_words = len(self.ngrams)
        self.invrank = {
            gram:( n_words - rank )
            for gram,rank in self.ngrams.iteritems()
        }

    def compare_tc(self, unknown_text, normaliser):
        # Implements line 442 of text_cat.pl, where
        # normaliser is results[language] from CharModel
        if normaliser <= 0:
            return normaliser
        else:
            unknown_freq = self.freq_of_text(unknown_text, {})
            return (
                sum(
                    self.invrank[word]**2 * unknown_freq[word] * 100 / normaliser

                    for word in unknown_freq.keys()
                    if word in self.ngrams
                )
            )

class Classifier(object):
    DROP_RATIO = 1.10

    def __init__(self, folder, langs=[], verbose=False):
        self.cmodels = {}
        self.wmodels = {}

        ext = '.lm'
        fnames = []
        folder_glob = os.path.join(folder, '*'+ext)
        found_fnames = glob.glob(os.path.normcase(folder_glob))
        if len(found_fnames) == 0:
            raise ValueError("No language files found in %s" % (folder,))

        if len(langs) == 0:
            fnames = found_fnames
        else:
            fnames = [os.path.join(folder, lang+ext) for lang in langs]
            not_found = set(fnames) - set(found_fnames)
            if len(not_found) != 0:
                raise ValueError("Unknown language(s): " + ", ".join(not_found))

        for fname in fnames:
            lang = basename_noext(fname, ext)
            self.cmodels[lang] = CharModel(lang).of_model_file(fname)
            if verbose:
                print "Loaded %s" % (fname,)

            fname_wm = os.path.join(folder, lang+'.wm')
            if os.path.exists(fname_wm):
                self.wmodels[lang] = WordModel(lang).of_model_file(fname_wm)
                if verbose:
                    print "Loaded %s" % (fname_wm,)
            else:
                self.wmodels[lang] = WordModel(lang).of_freq({})


    def classify_full(self, intext):
        if len(self.cmodels) == 0:
            return [('guess', 0)]
        else:
            if type(intext) == str:
                text = intext.decode('utf-8')
            else:
                text = intext
            ingram = CharModel().of_text(text)

            cscored = { l:model.compare(ingram)
                        for l,model in self.cmodels.iteritems() }
            cranked = sort_by_value(cscored)
            cbest = cranked[0]
            cfiltered = [ (l,d) for l,d in cranked
                         if d <= cbest[1] * self.DROP_RATIO ]
            if len(cfiltered) <= 1:
                return cfiltered
            else:
                # Along with compare_tc, implements text_cat.pl line
                # 442 and on:
                wscored = { l:model.compare_tc(text, cscored[l])
                            for l,model in self.wmodels.iteritems() }
                cwcombined = { l:( cscored[l] - wscore )
                             for l,wscore in wscored.iteritems() }
                cwranked = sort_by_value( cwcombined )
                return cwranked


    def classify(self, text):
        return self.classify_full(text)[0][0]


class Trainer(object):
    def __init__(self, folder, ext='.txt', Model=CharModel, verbose=False):
        self.models = {}
        folder_glob = os.path.join(folder, '*'+ext)

        for fname in glob.glob(os.path.normcase(folder_glob)):
            if verbose:
                msg = "Processing %s" % (fname,)
                if os.path.getsize(fname) > 5000000:
                    msg += " (this may take a while)"
                print msg.encode('utf-8')
                sys.stdout.flush()
            lang = basename_noext(fname, ext)
            self.models[lang] = Model(lang).of_text_file(open(fname, 'r'))
        if len(self.models) == 0:
            raise Exception("No suitable files found matching %s!" % (folder_glob,))

    def save(self, folder, ext='.lm', verbose=False):
        for lang, model in self.models.iteritems():
            fname = os.path.join(folder, lang+ext)
            model.to_model_file(fname)
        if verbose and len(self.models) != 0:
            print ("Wrote {%s}%s" % (",".join(self.models.keys()),ext)).encode('utf-8')



if __name__ == "__main__":
    # TODO: real argparser, check if outdir exists first so we don't process a bunch and then die :>
    Trainer(sys.argv[1], Model=CharModel, verbose=True).save(sys.argv[2], ext='.lm', verbose=True)
    Trainer(sys.argv[1], Model=WordModel, verbose=True).save(sys.argv[2], ext='.wm', verbose=True)
