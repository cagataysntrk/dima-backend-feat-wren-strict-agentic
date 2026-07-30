"""dima-admin-api — superadmin control-plane servisi (ADR-0015).

Public `dima-api` ile AYRI deployable; ortak mantık `control_plane`'den gelir.
Bu paket **public `app/` paketini import etmez** (yalnız hafif `app.config`'i dolaylı,
`control_plane` üzerinden). Route'lar `/sadmin/*`; hepsi superadmin-only.
"""

__version__ = "0.1.0"
