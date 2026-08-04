"""Private model submodules — fachliche Cluster der Domain-Modelle.

Dieses Paket ist bewusst privat (``_models``): Der stabile öffentliche
Einstiegspunkt ist ``numerology_domain.models`` (Compatibility Facade), die
direkt aus den einzelnen Cluster-Submodulen importiert
(``_models.calculation``, ``_models.cycles``, ``_models.input``,
``_models.profile``) statt aus diesem Aggregator.

Dieses ``__init__.py`` re-exportiert absichtlich nichts: Ein früherer
Aggregator-Export hier duplizierte 72 Zeilen aus ``models.py``, ohne von
irgendeinem Konsumenten importiert zu werden (kein Treffer für
``numerology_domain._models`` außerhalb der Submodul-Importe selbst). Jede
Vertragserweiterung musste dadurch an zwei Stellen nachgezogen werden, ohne
dass die zweite Stelle je wirksam war. Direkte Imports aus den einzelnen
Submodulen (``numerology_domain._models.calculation`` etc.) bleiben für
interne Zwecke erlaubt, sind aber nicht Teil des öffentlichen Vertrags.
"""
