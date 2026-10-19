# Cervecería Los Flacheros — Frontend

Frontend del proyecto (Next.js con App Router, Tailwind y JavaScript puro).

Esta carpeta la completa el otro integrante del grupo, Ema. La API que consume
está documentada en [`../tasks/api-contract.md`](../tasks/api-contract.md).

El backend corre en `http://localhost:8000` y expone el token en `POST /api/auth-token/`.
El frontend debe consumir **solo** con el header `Authorization: Token <key>` y nunca
con login por sesión (las cookies comparten puerto entre `localhost:3000` y `localhost:8000`).
