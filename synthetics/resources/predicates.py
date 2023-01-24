import re
import glob
from typing import Optional
from tqdm import tqdm
from xml.etree.ElementTree import ElementTree, ParseError


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
        return f'<{self.__class__.__name__} → id: {self.frame_id}, roleset: {list(self.roleset.keys())}>'

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


class Lexicon:
    def __init__(self, filepath: str = 'D:/Corpora & Language Resources/modu-corenlp/framefiles/*/*.xml'):
        self.frame_files: list = glob.glob(filepath)
        self.lemma_to_frames: dict[str, set] = dict()
        self.form_to_frames: dict[str, set] = dict()

    def add_form(self, form: str, frame: VerbFrame):
        if form not in self.form_to_frames:
            self.form_to_frames[form] = set()
        self.form_to_frames[form].add(frame)

    def add_frame(self, lemma: str, frame: VerbFrame):
        if lemma not in self.lemma_to_frames:
            self.lemma_to_frames[lemma] = set()
        self.lemma_to_frames[lemma].add(frame)

    def from_files(self, pickle: str = 'frameset.pkl'):
        for filename in tqdm(self.frame_files):
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
                    edef = frameset.find('edef').text.strip() if frameset.find('edef') else None
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
                                self.add_form(form=rel, frame=entry)
                        self.add_frame(lemma=lemma, frame=entry)
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
                            self.add_form(form=rel, frame=entry)
                        self.add_frame(lemma=lemma, frame=entry)
                    elif source == 'modu':
                        kdef = frameset.find('kdef').text.strip()
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
                            self.add_form(form=rel, frame=entry)
                        self.add_frame(lemma=lemma, frame=entry)
                    else:
                        raise ValueError


if __name__ == '__main__':
    lexicon = Lexicon('D:/Corpora & Language Resources/modu-corenlp/framefiles/*/*.xml')
    lexicon.from_files()

    for form, frames in lexicon.form_to_frames.items():
        print(form, frames)
