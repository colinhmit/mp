import spacy

from src.utils._functions_general import *


class NLPParser:
    def __init__(self):
        self.SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
        self.OBJECTS = ["dobj", "dative", "attr", "oprd"]
        self.ADJECTIVES = ["amod", "acomp"]
        self.parser = spacy.load('en')
        self.parser.vocab.strings.set_frozen(True)
        pp('nlp: Initialized.')

    def parse_text(self, text):
        parsed_text = self.parser(unicode(text))
        svos = self.parse_SVOs(parsed_text)
        subjs = self.parse_subjs(parsed_text)
        return {'svos': svos, 'subjects': subjs}

    def flush(self):
        self.parser.vocab.strings.flush_oov()

    # SVO Methodology
    def get_subs_from_conjs(self, subs):
        more_subs = []
        for sub in subs:
            # rights is a generator
            rights = list(sub.rights)
            right_deps = {tok.lower_ for tok in rights}
            if "and" in right_deps:
                more_subs.extend([tok for tok in rights
                                  if tok.dep_ in self.SUBJECTS or tok.pos_ == "NOUN"])
                if len(more_subs) > 0:
                    more_subs.extend(self.get_subs_from_conjs(more_subs))
        return more_subs

    def get_objs_from_conjs(self, objs):
        more_objs = []
        for obj in objs:
            # rights is a generator
            rights = list(obj.rights)
            right_deps = {tok.lower_ for tok in rights}
            if "and" in right_deps:
                more_objs.extend([tok for tok in rights
                                  if tok.dep_ in self.OBJECTS or tok.pos_ == "NOUN"])
                if len(more_objs) > 0:
                    more_objs.extend(self.get_objs_from_conjs(more_objs))
        return more_objs

    def get_verbs_from_conjs(self, verbs):
        more_verbs = []
        for verb in verbs:
            right_deps = {tok.lower_ for tok in verb.rights}
            if "and" in right_deps:
                more_verbs.extend([tok for tok in verb.rights if tok.pos_ == "VERB"])
                if len(more_verbs) > 0:
                    more_verbs.extend(self.get_verbs_from_conjs(more_verbs))
        return more_verbs

    def find_subs(self, tok):
        head = tok.head
        while (head.pos_ != "VERB" and head.pos_ != "NOUN" and head.head != head):
            head = head.head
        if head.pos_ == "VERB":
            subs = [tok for tok in head.lefts if tok.dep_ == "SUB"]
            if len(subs) > 0:
                verb_negated = self.is_negated(head)
                subs.extend(self.get_subs_from_conjs(subs))
                return subs, verb_negated
            elif head.head != head:
                return self.find_subs(head)
        elif head.pos_ == "NOUN":
            return [head], self.is_negated(tok)
        return [], False

    def is_negated(self, tok):
        negations = {"no", "not", "n't", "never", "none"}
        for dep in list(tok.lefts) + list(tok.rights):
            if dep.lower_ in negations:
                return True
        return False

    def find_SVs(self, tokens):
        svs = []
        verbs = [tok for tok in tokens if tok.pos_ == "VERB"]
        for v in verbs:
            subs, verb_negated = get_all_subs(v)
            if len(subs) > 0:
                for sub in subs:
                    svs.append((sub.orth_, "!" + v.orth_ if verb_negated else v.orth_))
        return svs

    def get_objs_from_prepos(self, deps):
        objs = []
        for dep in deps:
            if dep.pos_ == "ADP" and dep.dep_ == "prep":
                objs.extend([tok for tok in dep.rights
                             if tok.dep_ in self.OBJECTS or
                             (tok.pos_ == "PRON" and tok.lower_ == "me")])
        return objs

    def get_objs_from_attr(self, deps):
        for dep in deps:
            if dep.pos_ == "NOUN" and dep.dep_ == "attr":
                verbs = [tok for tok in dep.rights if tok.pos_ == "VERB"]
                if len(verbs) > 0:
                    for v in verbs:
                        rights = list(v.rights)
                        objs = [tok for tok in rights if tok.dep_ in self.OBJECTS]
                        objs.extend(self.get_objs_from_prepos(rights))
                        if len(objs) > 0:
                            return v, objs
        return None, None

    def get_objs_from_xcomp(self, deps):
        for dep in deps:
            if dep.pos_ == "VERB" and dep.dep_ == "xcomp":
                v = dep
                rights = list(v.rights)
                objs = [tok for tok in rights if tok.dep_ in self.OBJECTS]
                objs.extend(self.get_objs_from_prepos(rights))
                if len(objs) > 0:
                    return v, objs
        return None, None

    def get_all_subs(self, v):
        verb_negated = self.is_negated(v)
        subs = [tok for tok in v.lefts if tok.dep_ in self.SUBJECTS and tok.pos_ != "DET"]
        if len(subs) > 0:
            subs.extend(self.get_subs_from_conjs(subs))
        else:
            found_subs, verb_negated = self.find_subs(v)
            subs.extend(found_subs)
        return subs, verb_negated

    def get_all_objs(self, v):
        # rights is a generator
        rights = list(v.rights)
        objs = [tok for tok in rights if tok.dep_ in self.OBJECTS]
        objs.extend(self.get_objs_from_prepos(rights))

        # potentialNewVerb, potentialNewObjs = getObjsFromAttrs(rights)
        # if potentialNewVerb is not None and potentialNewObjs is not None
        #                                        and len(potentialNewObjs) > 0:
        #    objs.extend(potentialNewObjs)
        #    v = potentialNewVerb

        new_verb, new_objs = self.get_objs_from_xcomp(rights)

        if (new_verb is not None and new_objs is not None and len(new_objs) > 0):
            objs.extend(new_objs)
            v = new_verb
        if len(objs) > 0:
            objs.extend(self.get_objs_from_conjs(objs))
        return v, objs

    def parse_SVOs(self, tokens):
        svos = []
        verbs = [tok for tok in tokens if tok.pos_ == "VERB" and tok.dep_ != "aux"]
        for v in verbs:
            subs, verb_negated = self.get_all_subs(v)
            # hopefully there are subs, if not, don't examine this verb
            if len(subs) > 0:
                v, objs = self.get_all_objs(v)
                for sub in subs:
                    for obj in objs:
                        # objNegated = self.isNegated(obj)
                        # svos.append((sub,v,obj,verbNegated))
                        svos.append({'subj':    sub.lower_,
                                     'verb':    v.vector,
                                     'obj':     obj.vector,
                                     'neg':     verb_negated})
        return svos

    def parse_subjs(self, tokens):
        adjs = [tok.lower_ for tok in tokens if tok.dep_ in self.ADJECTIVES]
        subs = [{'lower':   tok.lower_,
                 'vector':  tok.vector,
                 'adjs':    adjs}
                for tok in tokens if tok.dep_ in self.SUBJECTS]
        return subs
