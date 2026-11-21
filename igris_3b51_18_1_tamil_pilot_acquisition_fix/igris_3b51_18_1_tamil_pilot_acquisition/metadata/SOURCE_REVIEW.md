# Source review

IndicCorpV2 dataset card declares datasets created in the work as CC0.
Tamil file: `data/ta.txt` (11.8 GB as listed on Hugging Face).
The dataset viewer `/rows` endpoint documents support for datasets with
Parquet exports; this repository exposes a plain-text file. The HTTP 501 from
the previous script is therefore consistent with an unsupported viewer feature.

References:
- https://huggingface.co/datasets/ai4bharat/IndicCorpV2
- https://huggingface.co/datasets/ai4bharat/IndicCorpV2/blob/main/data/ta.txt
- https://huggingface.co/docs/dataset-viewer/rows

Commercial-use caveat: a dataset-level CC0 statement does not by itself
resolve every possible third-party rights or provenance issue.
