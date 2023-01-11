# korean-amr-synthetics
Automatic data augmentation for Korean AMR

### *Statistics of `modu-corpora`*
- `cr-dep-el-ner-pos-srl-wsd-za`: 150,082 items *(Target of Annotation Synthesis)*
- `cr-dep-wsd-za`: 221,489 items
- `el-ner`: 1,741,546 items
- `el-ner-pos`: 223,962 items
- `wsd`: 123,636 items

### *Steps*
1) DEP로 `penman`으로 인코딩
2) 두 어절 이상에 걸친 우언적 구성을 기준으로 어절 군집화
3) POS + WSD 활용하여 node 내부에 내용어와 기능어 분리
4) NER + EL 적용
5) SRL 적용
6) ZA, CR 적용