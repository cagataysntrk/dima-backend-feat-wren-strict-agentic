"""Public dima-api auth surface (login/refresh/logout/me) + request principal.

İş mantığı ``control_plane`` çekirdeğinden gelir (ADR-0015 Karar 1: ortak kod route
yaymayan ``control_plane``'de). Bu paket yalnız HTTP kabuğu + FastAPI dependency.
"""
