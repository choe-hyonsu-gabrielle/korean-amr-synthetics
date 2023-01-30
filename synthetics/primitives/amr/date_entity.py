import re
from typing import Any, Optional
from synthetics.primitives.amr.concept import AMRIndexFreeConcept


class AMRDateEntityConcept(AMRIndexFreeConcept):
    ### covers DT_DAY, DT_WEEK, DT_MONTH, DT_YEAR, DT_SEASON
    def __init__(
            self,
            concept_type: str,
            entity_idx: Any,
            entity_str: str,
            wiki: Optional[str] = None,
            mapping: Optional[set[int]] = None
    ):
        self.entity_str: str = re.sub(r'\s+', ' ', entity_str.strip())
        super().__init__(concept_type='-'.join(self.entity_str.split()), mapping=mapping)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.concept_type} → "{self.entity_str}" {self.mapping}>'

    def product(self, global_idx: Any) -> list:
        return super().product(global_idx=global_idx)


class AMRDateIntervalConcept(AMRIndexFreeConcept):
    def __init__(
            self,
            concept_type: str,
            entity_idx: Any,
            entity_str: str,
            wiki: Optional[str] = None,
            mapping: Optional[set[int]] = None
    ):
        self.entity_str: str = re.sub(r'\s+', ' ', entity_str.strip())
        super().__init__(concept_type='-'.join(self.entity_str.split()), mapping=mapping)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.concept_type} → "{self.entity_str}" {self.mapping}>'

    def product(self, global_idx: Any) -> list:
        return super().product(global_idx=global_idx)
