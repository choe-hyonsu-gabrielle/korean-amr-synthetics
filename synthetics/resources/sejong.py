import re
import time
import glob
from xml.etree.ElementTree import ElementTree
from typing import Optional, Union
from tqdm import tqdm
from synthetics.utils import save_pickle, load_pickle, timestamp


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
    return [tuple(tht_rol.split('=')) for tht_rol in desc.strip().split()]


def parse_selective_restriction(desc: str):
    pass


class IdiomaticVerbFrames(Lexicon):
    def __init__(self):
        super().__init__()
        self.entries: dict[str, VerbFrame] = dict()

    def add_entry(self, item: VerbFrame):
        self.entries[item.frame] = item

    def from_files(self, files: Union[str, list[str], set[str], tuple[str]]):

        all_temp = set()
        all_sel_rst = set()
        all_tht_rol = set()

        target_files = []
        if isinstance(files, str):
            target_files.extend(glob.glob(files))
        elif isinstance(files, (list, set, tuple)):
            for item in files:
                target_files.extend(glob.glob(item))
        for target in tqdm(target_files, desc=f'{self} - loading {len(target_files)} files'):
            xml = ElementTree(file=target)
            root = xml.getroot()
            orth = root.find('orth').text.strip()
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
                        if theta:
                            print(frame_name, template, theta, selective, parse_theta_role(theta))
                            all_temp.add(template)
                            all_tht_rol.update(parse_theta_role(theta))
                            all_sel_rst.add(selective)
                            self.add_entry(entry)
                        else:
                            print(frame_name, template, theta, selective)
        print(all_temp)
        print(all_sel_rst)
        print(all_tht_rol)
        pass

    @staticmethod
    def from_pickle(filename):
        start = time.time()
        lexicon: IdiomaticVerbFrames = load_pickle(filename)
        lapse = time.time() - start
        print(f'- unpickling `{filename}`, {lapse:.2f} sec lapsed, {len(lexicon)} Entry items:', end=' ')
        print(lexicon)
        return lexicon

if __name__ == '__main__':
    idioms = "/Users/choe.hyonsu.gabrielle/modu-corenlp-essential/sejong/01_전자사전/XML파일/상세전자사전/15. 관용표현_상세/1/*.xml"

    frameset = IdiomaticVerbFrames()
    frameset.from_files(files=idioms)
    