import re
import glob
from typing import Optional
from tqdm import tqdm
from xml.etree.ElementTree import ElementTree, ParseError
from synthetics.rules.verbalizations import VERBALIZATIONS


class VerbFrame:
    def __init__(self, filename: str, lemma: str, frame_id: str, edef: Optional[str] = None, kdef: Optional[str] = None):
        self.filename: str = filename
        self.lemma: str = lemma
        self.frame_id: str = frame_id
        self.edef: Optional[str] = edef
        self.kdef: Optional[str] = kdef
        self.roleset: dict = dict()
        self.mappings: dict = dict()

    def __repr__(self):
        return f'<{self.__class__.__name__} → id: {self.frame_id}, edef: "{self.edef}", roleset: {tuple(self.roleset.keys())}>'

    def add_argrole(self, argnum: str, argrole: str):
        assert re.search(r'^[\dA]$', argnum), print(f'argnum="{argnum}"')
        key = 'ARG' + argnum
        if key in self.roleset:
            self.roleset[key] += ' | ' + argrole.strip()
        else:
            self.roleset[key] = argrole.strip()

    def add_mapping(self, rel: str, src: str, trg: str):
        if rel not in self.mappings:
            self.mappings[rel] = dict()
        if trg in self.mappings[rel]:
            self.mappings[rel][trg] = src
        else:
            self.mappings[rel][trg] = dict()
            self.mappings[rel][trg] = src


class PropBankFrame(VerbFrame):
    def __init__(self, filename: str, lemma: str, frame_id: str, edef: Optional[str] = None, kdef: Optional[str] = None):
        super().__init__(filename, lemma, frame_id, edef, kdef)


class ETRIFrame(VerbFrame):
    def __init__(self, filename: str, lemma: str, frame_id: str, edef: Optional[str] = None, kdef: Optional[str] = None):
        super().__init__(filename, lemma, frame_id, edef, kdef)


class ModuFrame(VerbFrame):
    def __init__(self, filename: str, lemma: str, frame_id: str, edef: Optional[str] = None, kdef: Optional[str] = None):
        super().__init__(filename, lemma, frame_id, edef, kdef)


class VerbFrameLexicon:
    instance = None
    intact = True

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, filepath: str = 'D:/Corpora & Language Resources/modu-corenlp/framefiles/*/*.xml'):
        if VerbFrameLexicon.intact:
            self.frame_files: list = glob.glob(filepath)
            self.entries: dict = dict()
            self.root_to_frames: dict[str, list] = dict()
            self.lemma_to_frames: dict[str, list] = dict()
            self.from_files()
            VerbFrameLexicon.intact = False

    def add_lemma(self, lemma_form: str, frame: VerbFrame):
        if lemma_form not in self.lemma_to_frames:
            self.lemma_to_frames[lemma_form] = list()
        self.lemma_to_frames[lemma_form].append(frame)

    def add_frame(self, root_form: str, frame: VerbFrame):
        if root_form not in self.root_to_frames:
            self.root_to_frames[root_form] = list()
        self.root_to_frames[root_form].append(frame)

    def get_frames_by_lemma(self, lemma_form: str):
        if lemma_form in self.lemma_to_frames:
            return self.lemma_to_frames[lemma_form]
        elif lemma_form in VERBALIZATIONS:
            return self.get_frames_by_lemma(VERBALIZATIONS[lemma_form].split('-')[0])
        else:
            return None

    def get_frames_by_root(self, root_form: str):
        if root_form in self.root_to_frames:
            return self.root_to_frames[root_form]
        elif root_form in VERBALIZATIONS:
            return self.get_frames_by_root(VERBALIZATIONS[root_form].split('-')[0])
        else:
            return None

    def from_files(self):
        for filename in tqdm(self.frame_files, desc='- loading verb frame files'):
            _dir, source, xml_file = filename.split('\\')

            try:
                root = ElementTree(file=filename).getroot()
            except ParseError as e:
                print(filename)
                raise e

            for predicate in root.findall('predicate'):
                lemma = predicate.find('lemma').text.strip()
                for frameset in predicate.findall('frameset'):
                    frame_id = frameset.find('id').text.strip()
                    frame_id = frame_id.replace('.', '-')
                    frame_id = '-'.join(frame_id.split())
                    edef = frameset.find('edef').text
                    if source == 'kpb':
                        entry = PropBankFrame(filename=filename, lemma=lemma, frame_id=frame_id, edef=edef)
                        for role in frameset.find('roleset'):
                            kwargs = {k: v for k, v in role.items()}
                            entry.add_argrole(**kwargs)
                        for frame in frameset.findall('frame'):
                            mapping = frame.find('mapping')
                            if mapping.find(''):
                                rel = mapping.find('rel').text.strip()
                                for mapitem in mapping.findall('mapitem'):
                                    src = mapitem.get('src')
                                    trg = mapitem.get('trg')
                                    entry.add_mapping(rel=rel, src=src, trg=trg.upper())
                                self.add_lemma(lemma_form=rel, frame=entry)
                        self.add_frame(root_form=lemma, frame=entry)
                        self.entries[entry.frame_id] = entry
                    elif source == 'etri':
                        entry = ETRIFrame(filename=filename, lemma=lemma, frame_id=frame_id, edef=edef)
                        for role in frameset.find('roleset'):
                            kwargs = {k: v for k, v in role.items()}
                            entry.add_argrole(**kwargs)
                        for frame in frameset.findall('frame'):
                            mapping = frame.find('mapping')
                            rel = mapping.find('rel').text.strip()
                            for mapitem in mapping.findall('mapitem'):
                                src = mapitem.get('src')
                                trg = mapitem.get('trg')
                                entry.add_mapping(rel=rel, src=src, trg=trg.upper())
                            self.add_lemma(lemma_form=rel, frame=entry)
                        self.add_frame(root_form=lemma, frame=entry)
                        self.entries[entry.frame_id] = entry
                    elif source == 'modu':
                        kdef = frameset.find('kdef').text
                        entry = ModuFrame(filename=filename, lemma=lemma, frame_id=frame_id, edef=edef, kdef=kdef)
                        for role in frameset.find('roleset'):
                            kwargs = {k: v for k, v in role.items()}
                            entry.add_argrole(**kwargs)
                        for frame in frameset.findall('frame'):
                            mapping = frame.find('mapping')
                            rel = mapping.find('rel').text.strip().split('.')[0]
                            for mapitem in mapping.findall('mapitem'):
                                src = mapitem.get('src')
                                trg = mapitem.get('trg')
                                entry.add_mapping(rel=rel, src=src, trg=re.sub(r'\s+', '', trg))
                            self.add_lemma(lemma_form=rel, frame=entry)
                        self.add_frame(root_form=lemma, frame=entry)
                        self.entries[entry.frame_id] = entry
                    else:
                        raise ValueError


if __name__ == '__main__':
    lexicon = VerbFrameLexicon()

    with open('frame-list.txt', encoding='utf-8', mode='w') as fp:
        for form, frames in lexicon.entries.items():
            print(form, frames)
            print(form + '\t' + str(frames), file=fp)
        print(len(lexicon.entries))
        print(len(lexicon.root_to_frames))
