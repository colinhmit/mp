# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:55:12 2016

@author: colinh
"""
import spacy
from functions_general import *

class nlpParser:

    def __init__(self): 
        pp('Initializing nlpParser...')
        self.SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
        self.OBJECTS = ["dobj", "dative", "attr", "oprd"]
        self.parser = spacy.load('en')
        self.parser.vocab.strings.set_frozen(True)
        pp('Initialized nlpParser.')

    def parse_text(self,text):
        parsed_text = self.parser(unicode(text))
        return self.findSVOs(parsed_text)

    def flush(self):
        self.parser.vocab.strings.flush_oov()

    #SVO Methodology
    def getSubsFromConjunctions(self,subs):
        moreSubs = []
        for sub in subs:
            # rights is a generator
            rights = list(sub.rights)
            rightDeps = {tok.lower_ for tok in rights}
            if "and" in rightDeps:
                moreSubs.extend([tok for tok in rights if tok.dep_ in self.SUBJECTS or tok.pos_ == "NOUN"])
                if len(moreSubs) > 0:
                    moreSubs.extend(self.getSubsFromConjunctions(moreSubs))
        return moreSubs

    def getObjsFromConjunctions(self,objs):
        moreObjs = []
        for obj in objs:
            # rights is a generator
            rights = list(obj.rights)
            rightDeps = {tok.lower_ for tok in rights}
            if "and" in rightDeps:
                moreObjs.extend([tok for tok in rights if tok.dep_ in self.OBJECTS or tok.pos_ == "NOUN"])
                if len(moreObjs) > 0:
                    moreObjs.extend(self.getObjsFromConjunctions(moreObjs))
        return moreObjs

    def getVerbsFromConjunctions(self,verbs):
        moreVerbs = []
        for verb in verbs:
            rightDeps = {tok.lower_ for tok in verb.rights}
            if "and" in rightDeps:
                moreVerbs.extend([tok for tok in verb.rights if tok.pos_ == "VERB"])
                if len(moreVerbs) > 0:
                    moreVerbs.extend(self.getVerbsFromConjunctions(moreVerbs))
        return moreVerbs

    def findSubs(self,tok):
        head = tok.head
        while head.pos_ != "VERB" and head.pos_ != "NOUN" and head.head != head:
            head = head.head
        if head.pos_ == "VERB":
            subs = [tok for tok in head.lefts if tok.dep_ == "SUB"]
            if len(subs) > 0:
                verbNegated = self.isNegated(head)
                subs.extend(self.getSubsFromConjunctions(subs))
                return subs, verbNegated
            elif head.head != head:
                return self.findSubs(head)
        elif head.pos_ == "NOUN":
            return [head], self.isNegated(tok)
        return [], False

    def isNegated(self,tok):
        negations = {"no", "not", "n't", "never", "none"}
        for dep in list(tok.lefts) + list(tok.rights):
            if dep.lower_ in negations:
                return True
        return False

    def findSVs(self,tokens):
        svs = []
        verbs = [tok for tok in tokens if tok.pos_ == "VERB"]
        for v in verbs:
            subs, verbNegated = getAllSubs(v)
            if len(subs) > 0:
                for sub in subs:
                    svs.append((sub.orth_, "!" + v.orth_ if verbNegated else v.orth_))
        return svs

    def getObjsFromPrepositions(self,deps):
        objs = []
        for dep in deps:
            if dep.pos_ == "ADP" and dep.dep_ == "prep":
                objs.extend([tok for tok in dep.rights if tok.dep_  in self.OBJECTS or (tok.pos_ == "PRON" and tok.lower_ == "me")])
        return objs

    def getObjsFromAttrs(self,deps):
        for dep in deps:
            if dep.pos_ == "NOUN" and dep.dep_ == "attr":
                verbs = [tok for tok in dep.rights if tok.pos_ == "VERB"]
                if len(verbs) > 0:
                    for v in verbs:
                        rights = list(v.rights)
                        objs = [tok for tok in rights if tok.dep_ in self.OBJECTS]
                        objs.extend(self.getObjsFromPrepositions(rights))
                        if len(objs) > 0:
                            return v, objs
        return None, None

    def getObjFromXComp(self,deps):
        for dep in deps:
            if dep.pos_ == "VERB" and dep.dep_ == "xcomp":
                v = dep
                rights = list(v.rights)
                objs = [tok for tok in rights if tok.dep_ in self.OBJECTS]
                objs.extend(self.getObjsFromPrepositions(rights))
                if len(objs) > 0:
                    return v, objs
        return None, None

    def getAllSubs(self,v):
        verbNegated = self.isNegated(v)
        subs = [tok for tok in v.lefts if tok.dep_ in self.SUBJECTS and tok.pos_ != "DET"]
        if len(subs) > 0:
            subs.extend(self.getSubsFromConjunctions(subs))
        else:
            foundSubs, verbNegated = self.findSubs(v)
            subs.extend(foundSubs)
        return subs, verbNegated

    def getAllObjs(self,v):
        # rights is a generator
        rights = list(v.rights)
        objs = [tok for tok in rights if tok.dep_ in self.OBJECTS]
        objs.extend(self.getObjsFromPrepositions(rights))

        #potentialNewVerb, potentialNewObjs = getObjsFromAttrs(rights)
        #if potentialNewVerb is not None and potentialNewObjs is not None and len(potentialNewObjs) > 0:
        #    objs.extend(potentialNewObjs)
        #    v = potentialNewVerb

        potentialNewVerb, potentialNewObjs = self.getObjFromXComp(rights)
        if potentialNewVerb is not None and potentialNewObjs is not None and len(potentialNewObjs) > 0:
            objs.extend(potentialNewObjs)
            v = potentialNewVerb
        if len(objs) > 0:
            objs.extend(self.getObjsFromConjunctions(objs))
        return v, objs

    def findSVOs(self,tokens):
        svos = []
        verbs = [tok for tok in tokens if tok.pos_ == "VERB" and tok.dep_ != "aux"]
        for v in verbs:
            subs, verbNegated = self.getAllSubs(v)
            # hopefully there are subs, if not, don't examine this verb any longer
            if len(subs) > 0:
                v, objs = self.getAllObjs(v)
                for sub in subs:
                    for obj in objs:
                        #objNegated = self.isNegated(obj)
                        #svos.append((sub,v,obj,verbNegated))
                        svos.append({'subj':sub.lower_,'verb':v.vector,'obj':obj.vector,'neg':verbNegated})
        return svos