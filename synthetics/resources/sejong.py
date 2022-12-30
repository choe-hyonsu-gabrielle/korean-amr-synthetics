import re
import time
import glob
from collections import defaultdict
from xml.etree.ElementTree import ElementTree
from typing import Optional, Union
from tqdm import tqdm
from synthetics.utils import save_pickle, load_pickle, timestamp
from synthetics.resources.stopitems import PRAGMATIC_IDIOMS


class Entry:
    def __init__(self, form: Optional[str] = None):
        self.form: Optional[str] = None
        pass


class VerbFrame(Entry):
    def __init__(self, form: Optional[str], frame: Optional[str]):
        super().__init__(form=form)
        self.frame: Optional[str] = frame
        self.lemma: Optional[str] = None
        self.edef: Optional[str] = None
        self.roleset: dict[str, str] = dict()
        self.examples: dict[str, set] = dict()


class Lexicon:
    def __init__(self):
        self.entries = dict()
        self.update = None

    def __len__(self):
        return len(self.entries)

    def __repr__(self):
        return f'<{self.__class__.__name__} → id: {id(self)}, update: {self.update}, entries: {len(self.entries)}>'

    def to_pickle(self, filename):
        # timestamp
        self.update = timestamp()
        save_pickle(filename=filename, instance=self)


def parse_theta_role(desc: str):
    if desc:
        return [tuple(tht_rol.split('=')) for tht_rol in desc.strip().split()]
    return [None]


def parse_selective_restriction(desc: str):
    pass


class IdiomaticVerbFrames(Lexicon):
    def __init__(self):
        super().__init__()
        self.entries: dict[str, VerbFrame] = dict()

    def add_entry(self, item: VerbFrame):
        self.entries[item.frame] = item

    def from_files(self, files: Union[str, list[str], set[str], tuple[str]]):

        all_temp = defaultdict(set)
        all_sel_rst = defaultdict(set)
        all_tht_rol = defaultdict(set)

        target_files = []
        if isinstance(files, str):
            target_files.extend(glob.glob(files))
        elif isinstance(files, (list, set, tuple)):
            for item in files:
                target_files.extend(glob.glob(item))
        target_files = [f for f in target_files if f.split('\\')[-1] not in PRAGMATIC_IDIOMS]

        for target in tqdm(target_files, desc=f'{self} - loading {len(target_files)} files'):
            xml = ElementTree(file=target)
            root = xml.getroot()
            orth = re.sub(r'\s+', ' ', root.find('orth').text.strip())
            edef = None  # trans
            morph_grp = root.find('entry').find()
            for sense in list(root.find('entry').findall('sense')):
                frame_name = '-'.join(orth.split() + [sense.attrib.get('n').zfill(2)])
                entry = VerbFrame(form=orth, frame=frame_name)
                for frame in sense.find('syn_grp').findall('frame_grp'):
                    template = frame.find('frame').text
                    entry.examples[template] = set()
                    for syn_sem in frame.findall('syn_sem'):
                        examples = [eg.text.strip() for eg in syn_sem.findall('eg') if eg]
                        entry.examples[template].update(examples)
                        theta = syn_sem.find('tht_rol').text
                        selective = syn_sem.find('sel_rst').text

                        all_temp[template].add(orth)
                        for tup in parse_theta_role(theta):
                            all_tht_rol[tup].add(orth)
                        all_sel_rst[selective].add(orth)

                        self.add_entry(entry)

                        if not theta:
                            print(frame_name, template, theta, selective)

        with open('templetes.tsv', encoding='utf-8', mode='w') as fp:
            for k, v in all_temp.items():
                print(f'{k}', file=fp)

        with open('selectives.tsv', encoding='utf-8', mode='w') as fp:
            for k, v in all_sel_rst.items():
                print(f'{k}', file=fp)

        with open('theta-roles.tsv', encoding='utf-8', mode='w') as fp:
            for k, v in all_tht_rol.items():
                print(f'{k}\t{v}', file=fp)

        print(len(self.entries))

    @staticmethod
    def from_pickle(filename):
        start = time.time()
        lexicon: IdiomaticVerbFrames = load_pickle(filename)
        lapse = time.time() - start
        print(f'- unpickling `{filename}`, {lapse:.2f} sec lapsed, {len(lexicon)} Entry items:', end=' ')
        print(lexicon)
        return lexicon


if __name__ == '__main__':
    # idioms = "/Users/choe.hyonsu.gabrielle/modu-corenlp-essential/sejong/01_전자사전/XML파일/상세전자사전/15. 관용표현_상세/1/*.xml"
    idioms = 'D:/Corpora & Language Resources/modu-corenlp/sejong/XML파일/상세전자사전/15. 관용표현_상세/1/*.xml'

    frameset = IdiomaticVerbFrames()
    frameset.from_files(files=idioms)
    