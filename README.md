# DI-Software-Gruppe-SJJL
Group project for FH Wien Digital Innovation – Software Engineering final assignment.

Flappy-Bee: Endless Runner mit Twist
Projektbeschreibung
Dies ist eine einfache Flappy-Bird-Variante als Endless Runner, bei der der Spieler einen fliegenden Vogel (bzw. eine Biene) steuert, der durch scrollende Rohre mit zufällig platzierten Lücken fliegen muss. Das Ziel ist es, möglichst viele Punkte durch erfolgreiches Durchfliegen zu sammeln. Der Clou (USP) sind besondere Power-Ups (z.B. Schild oder Speed-Boost) und ein Tag-/Nacht-Wechsel, der die Schwierigkeit dynamisch steigert.
Kernfeatures
	•	Fliegender Vogel mit Jump-Physik, Gravitation und Flügelschlag-Animation
	•	Scrollende Rohre mit zufälligen Lücken und Kollisionserkennung
	•	Punktesystem für erfolgreiches Durchfliegen der Rohre
	•	Start-, Game-Over-Screens und scrollender Hintergrund sowie Boden
	•	USP: Power-Ups (wie Schild oder Speed-Boost) und Tag-/Nacht-Wechsel für dynamische Schwierigkeit
Technik
	•	Haupt-Framework: Pygame (für Sprites, Events, Kollisionen, 60 FPS Game Loop)
	•	Python-Bibliotheken: random (für Rohrgenerierung), os (für Asset-Verwaltung)
	•	Grafiken: Einfache PNG-Sprites (Vogel-Animation, Rohre, Hintergrund), frei online erhältlich
	•	Aufbau: Klassen für Bird, Pipe, Game-World mit ca. 200-400 Zeilen Code in der Basisversion
Entwicklungsaufwand
	•	Basisversion: ca. 4-8 Stunden Programmierzeit
	•	Mit USP, Zusatzfeatures, Sound & Highscore-System: ca. 10-20 Stunden Gesamtaufwand
	•	Gut machbar als Teamprojekt, viele fertige Tutorials als Unterstützung verfügbar