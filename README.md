Projektname: EduCraft (Lehrer-Tool für Unterrichtsinhalte)

Beschreibung:
Das Lehrer-Tool für Unterrichtsinhalte ist eine webbasierte Anwendung, die Lehrkräften dabei hilft, Unterrichtsmaterialien zu erstellen, zu verwalten und mit Schülern zu teilen. Die Anwendung bietet eine intuitive Benutzeroberfläche, über die Lehrer Textdokumente hochladen, Fragen stellen und Antworten generieren können, um maßgeschneiderte Lerninhalte für ihre Schüler zu erstellen.

Funktionalitäten:

Materialerstellung: Lehrer können Textdokumente mit Lerninhalten im TXT- oder PDF-Format hochladen.
Fragenerstellung: Lehrer können Fragen zu den hochgeladenen Materialien formulieren, um das Verständnis der Schüler zu überprüfen.
Automatische Antwortgenerierung: Die Anwendung generiert automatisch Antworten auf die gestellten Fragen basierend auf den hochgeladenen Materialien und mithilfe von KI-Algorithmen.
Lernfortschritt-Tracking: Lehrer können den Lernfortschritt ihrer Schüler verfolgen und Feedback zu den bearbeiteten Materialien erhalten.
Benutzerverwaltung: Lehrer können Benutzerkonten für ihre Schüler erstellen und den Zugriff auf spezifische Materialien und Lernaktivitäten steuern.
Komponenten:

app.py: Enthält die Hauptlogik der Flask-App, einschließlich Routen für Datei-Upload, Fragenerstellung und Antwortgenerierung.
interface.py: Definiert die Schnittstellen-Endpunkte für die Kommunikation mit dem Frontend.
requirements.txt: Liste der erforderlichen Python-Bibliotheken und deren Versionen.
.env: Konfigurationsdatei für Umgebungsvariablen wie API-Schlüssel und Datenbank-Verbindungsdaten.
Technologien:

Python: Hauptprogrammiersprache für die Backend-Logik.
Flask: Web-Framework für die Erstellung der RESTful-API.
OpenAI: Integration für die Generierung von Antworten auf gestellte Fragen.
Supabase: Datenbank-Backend für die persistente Speicherung von Materialien und Lernaktivitäten.
Zielgruppe:
Lehrer und Bildungseinrichtungen, die nach einem benutzerfreundlichen Werkzeug suchen, um maßgeschneiderte Lerninhalte für ihre Schüler zu erstellen und deren Lernfortschritt zu verfolgen.

Installation und Ausführung:

Stelle sicher, dass Python und Pip auf deinem System installiert sind.
Installiere die erforderlichen Python-Bibliotheken aus der requirements.txt-Datei.
Führe die Flask-App aus, indem du python app.py im Terminal eingibst.
Lehrer und Schüler können die Anwendung über einen Webbrowser aufrufen und interagieren.
