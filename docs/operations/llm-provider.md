# Optionaler DeepSeek-Betrieb

Die deterministische Berechnung und die lokale Bibliothek funktionieren ohne
LLM. Der Provider ist standardmäßig deaktiviert.

## Konfiguration

```bash
NUMRA_LLM_ENABLED=false
NUMRA_DEEPSEEK_API_KEY=
NUMRA_DEEPSEEK_BASE_URL=https://api.deepseek.com
NUMRA_DEEPSEEK_MODEL=deepseek-v4-pro
NUMRA_REDIS_URL=redis://redis:6379/0
NUMRA_RATE_LIMIT_HMAC_SECRET=
```

Erst wenn `NUMRA_LLM_ENABLED=true` gesetzt wird, sind API-Schlüssel und ein
zufälliges HMAC-Secret zwingend. Das Secret sollte mindestens 32 zufällige
Bytes besitzen. API und Provider starten bei fehlender Konfiguration
absichtlich nicht.

## Datenschutzgrenze

An den Provider gehen ausschließlich der deterministische Profilhash,
Berechnungsreferenzen und Zahlen, Aussageklassen sowie die notwendigen Auszüge
aus `numra-knowledge-de-v1`. Klarname, aktiver Name, Geburtsdatum und
`input_ref` werden nicht in den Provider-Payload aufgenommen. Rückfragen werden
vor dem Provider-Aufruf auf Prompt-Injection, bekannte Profilnamen und
vollständige Datumsformen geprüft. Der vorhandene Bericht wird erneut an
Profilhash, Rechenwerte, Wissensreferenzen und Safety-Regeln gebunden; seine
Provenienz wird nicht an den Provider weitergereicht.

Provider-Ausgaben werden nur nach JSON-Schema-, Rechenwert-, Wissensreferenz-
und Safety-Validierung zurückgegeben. Leere oder ungültige Antworten werden
genau einmal wiederholt. Request-Bodies und Provider-Ausgaben dürfen niemals
protokolliert werden.

Der OpenAI-kompatible V4-Pro-Aufruf verwendet JSON Output, maximal 8.192
Ausgabetokens, `thinking.type=enabled` und `reasoning_effort=high`. Die
vereinbarte Sampling-Konfiguration `temperature=0.2` und `top_p=1` wird als
Provenienz geführt und aus Kompatibilitätsgründen gesendet. Laut offizieller
DeepSeek-Dokumentation werden beide Sampling-Parameter im Thinking-Modus
ignoriert; deshalb weist die Provenienz zusätzlich
`effective_sampling=provider_managed` und die wirksame Steuerung
`reasoning_effort=high` aus.

## Kontingente

- ein Bericht pro Gerät und Tag,
- zwei Rückfragen pro Gerät und Tag,
- zusätzlich 20 Provider-Aufrufe pro pseudonymisierter IP und Tag.

Redis erhält ausschließlich HMAC-Schlüssel mit Ablaufzeit. Roh-IP-Adressen,
Profile und Gespräche werden nicht gespeichert. Der öffentliche Host-Proxy
ersetzt eingehende `X-Forwarded-For`-Werte, und Uvicorn vertraut ausschließlich
der fest adressierten internen Gateway-Adresse `172.30.0.10`.

## Externes Launch-Gate

Ein Live-Smoke-Test wird erst mit einem echten API-Schlüssel ausgeführt. Vor
Aktivierung müssen Betreiber außerdem Drittlandtransfer, Vertragsgrundlage,
Provider-Datenschutzbedingungen und die sichtbare Einwilligung rechtlich
freigeben. Ohne diese Freigaben bleibt `NUMRA_LLM_ENABLED=false`.
