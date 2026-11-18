"""ihras -- reproducibility package for

  "Synergistic Integration of Deep Learning and Large Language Models for
   Explainable and Standardized Chest-Radiograph Diagnostics" (IHRAS).

Every result is COMPUTED from public data (NIH ChestX-ray14) and public model
weights (TorchXRayVision).  The values reported in the article are used ONLY as
references in ``ihras.compare``, which flags each item as MATCH, MISMATCH, or
NOT COMPUTED.  No article value is ever written as an output.
"""

__version__ = "1.0.0"
