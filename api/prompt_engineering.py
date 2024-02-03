
from typing import Any, Dict, List, Tuple
from langchain import hub

def unpack_prompt_input(input: Dict[str, Any]) -> Tuple[str, str, str, str, List[str], List[str]]:
    school_type = str(input.get("subject"))
    subject = str(input.get("subject"))
    topic = str(input.get("topic"))
    grade = str(input.get("grade"))
    state = str(input.get("state"))
    keywords = [str(i) for i in input.get("keywords")]
    context = [str(i) for i in input.get("context")]
    return school_type, subject, topic, grade, state, keywords, context


def create_output_table_format():
    return f"""{{
    "learn_goals": "xyz",
    "table_data": [
        {{"title": "abc", "duration": "10min", "content": "blabla"}},
        {{...}},
        {{...}}
    ]
}}    
"""

def create_task_string(school_type: str, subject: str, topic: str, grade: str, state: str, output_table_format) -> str:
    return f"""
Schritt 1: Plane eine Unterrichtsstunde im Fach {subject} zum Thema {topic} für eine {grade} Klasse in {state} für den Schultyp {school_type}!
Schritt 2: Formatiere deine Antwort in der folgenden json-Struktur: 
______________________________
{output_table_format}
______________________________

Antworte nicht außerhalb der dieser Struktur!

Los geht's!
"""

def pull_prompt_template(prompt_template_name): # custom fork from langsmith hub
    prompt = hub.pull(prompt_template_name)
    return prompt

def create_prompt_template(retrieved_context: List[Any], keywords, topic) -> str:
    keywords = '\n   -'.join(keywords)
    return f"""
Du bist ein Assistent für Lehrkräfte und deine Aufgabe ist Unterricht strukturiert, detailliert und fachlich korrekt vorzubereiten.

Lernziele:
------------------
- Thema: {topic}
- Schwerpunkte:
    {keywords}
------------------

Die Lehrkraft stellt dir Kontext zur Lösung der Aufgabe in deiner Bibliothek zur Verfügung. 
Hier ist ein kurzer Ausschnitt aus dem Kontext in deiner Bibliothek:

Ausschnitt aus dem Kontext:
---------
{retrieved_context}
---------

Wichtige Hinweise:

- Die Gesamtlänge des Unterrichts soll insgesamt 45 Minuten betragen.
- Alle Schritte der Aufgabe müssen ausgeführt werden.

Deine Aufgabe lautet:
"""