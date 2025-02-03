import os
import json
import openai

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print("🚨 Brak pliku config.json! Ustaw API OpenAI.")
    exit(1)

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

OPENAI_API_KEY = config["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

project_root = "RLdC_Trading_Bot_Final"

def analyze_code_with_gpt(code_snippet):
    """Analizuje kod przy użyciu GPT-4 Turbo i sugeruje ulepszenia"""
    prompt = f"""
    Oto kod źródłowy:

    {code_snippet}

    - Zidentyfikuj możliwe błędy, optymalizacje i ulepszenia
    - Zaproponuj nowe funkcje, które mogą zwiększyć efektywność kodu
    - Sugeruj aktualizacje zgodne z najnowszymi standardami

    Odpowiedź:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "Jesteś ekspertem w optymalizacji kodu i analizie jakości oprogramowania."},
                  {"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]

def scan_project_code():
    """Przeszukuje pliki w projekcie i analizuje kod źródłowy"""
    report = "📊 **AI Code Auditor - Raport Analizy** 📊\n\n"

    for root, _, files in os.walk(project_root):
        for file in files:
            if file.endswith(".py") or file.endswith(".sh") or file.endswith(".html"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    code_content = f.read()
                    analysis = analyze_code_with_gpt(code_content)
                    report += f"🔍 **Analiza: {file}**\n{analysis}\n\n"

    return report

if __name__ == "__main__":
    audit_report = scan_project_code()
    with open("ai_code_audit_report.txt", "w", encoding="utf-8") as f:
        f.write(audit_report)
    print("✅ AI Code Audit zakończony! Wyniki zapisane w ai_code_audit_report.txt")
