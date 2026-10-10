# 🎯 Job Search AI Agent & Skill (SuperJob Pro Edition)

Локальный автономный AI-агент и экспертный нейросетевой скилл для глубокого анализа IT-вакансий, расчетного скоринга (0–100 баллов), выявления скрытых рисков (Red Flags), генерации откликов по правилу первых 2 строк и комплексной подготовки к собеседованиям.

Архитектура и экспертные правила построены на стандартах портала работодателей и рекрутеров [SuperJob Pro](https://www.superjob.ru/pro/).

---

## 🌟 Форматы использования в нейросетевых средах

Агент спроектирован так, чтобы быть доступным в **любых современных AI-средах**:

1. **Native Skill в Google Antigravity**:
   - Находится в `.agents/skills/job-search-agent/SKILL.md` (в проекте) и в `~/.gemini/config/skills/job-search-agent/` (глобально для всех проектов).
   - Ассистент автоматически активирует скилл при запросах про вакансии, отклики, резюме и собеседования.
2. **Model Context Protocol (MCP)**:
   - Сервер `mcp_server.py` предоставляет стандартные инструменты (tools) для **Cursor**, **Windsurf**, **Claude Desktop**, **Antigravity**.
3. **Claude Code / Custom Assistants**:
   - Папка `.agents/skills/job-search-agent/` совместима со стандартами Skill-пакетов современных агентских CLI.
4. **Консольный запуск (CLI)**:
   - Автономные скрипты в `scripts/` и корневой `cli.py` для терминала и скриптов автоматизации.

---

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения (`.env`)
Файл `.env` уже сконфигурирован. При необходимости отредактируйте параметры:
```env
# Провайдер LLM: openai или gemini
LLM_PROVIDER=openai

# OpenAI (или совместимые шлюзы: OpenRouter, ProxyAPI, DeepSeek)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-6-luna
OPENAI_REASONING_EFFORT=medium

# Google Gemini (альтернатива)
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-3-flash
```

---

## 🔌 Подключение в AI-среды

### А. Google Antigravity / Gemini CLI
Скилл уже зарегистрирован:
- **Локально**: в `.agents/skills/job-search-agent/`
- **Глобально**: в `~/.gemini/config/skills/job-search-agent/`
- **Субагент**: зарегистрирован под именем `job_search_specialist`.

Для подключения MCP-инструментов в Antigravity добавьте секцию из `mcp_antigravity.json` в `~/.gemini/config/mcp_config.json`:
```json
{
  "mcpServers": {
    "job-search-agent": {
      "command": "python",
      "args": ["f:\\Downloads\\AI - Agents\\Job_Search_AI_Agent\\mcp_server.py"],
      "cwd": "f:\\Downloads\\AI - Agents\\Job_Search_AI_Agent"
    }
  }
}
```

### Б. Cursor / Windsurf
Добавьте в настройки MCP (`cursor_config.json` / Settings -> Features -> MCP Servers):
```json
{
  "mcpServers": {
    "job-search-agent": {
      "command": "python",
      "args": ["f:\\Downloads\\AI - Agents\\Job_Search_AI_Agent\\mcp_server.py"],
      "cwd": "f:\\Downloads\\AI - Agents\\Job_Search_AI_Agent"
    }
  }
}
```

### В. Anthropic Claude Desktop
В файле `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "job-search-agent": {
      "command": "python",
      "args": ["f:\\Downloads\\AI - Agents\\Job_Search_AI_Agent\\mcp_server.py"],
      "cwd": "f:\\Downloads\\AI - Agents\\Job_Search_AI_Agent"
    }
  }
}
```

---

## 🛠 Автономные инструменты MCP и CLI

Инструмент | Описание
:---|:---
`search_vacancies` | Мультипоиск по открытым API hh.ru, Хабр Карьере, ТрудВсем и каталогу стажировок (Сбер, Т-Банк, ИнфоТеКС, Яндекс).
`parse_vacancy` | Глубокий парсинг вакансии по ссылке (URL) или сырому тексту.
`score_vacancy` | Скоринг 0–100 по SuperJob Pro, выявление токсичности и штрафов за Red Flags.
`generate_cover_letter` | Генерация сопроводительного письма (правило 2 строк, ссылки на gorizont-blog.ru, без клише).
`prepare_interview` | 3 блока подготовки: 10 вопросов техскрининга, STAR-кейсы и вопросы работодателю.
`debrief_interview` | Разбор вопросов реального собеседования и план устранения пробелов.
`get_candidate_profile` | Верифицированный профиль кандидата Дмитрия Турейко (СПО МТИ).
`get_crm_funnel` | Текущая статистика воронки откликов в SQLite CRM.
`update_crm_status` | Смена статуса отклика (Новый -> Отправлено -> Скрининг -> Тестовое -> Оффер).

---

## 💻 Прямой запуск через терминал (CLI)

```bash
# 1. Поиск вакансий и стажировок
python .agents/skills/job-search-agent/scripts/search_jobs.py "Python стажер" --limit 5

# 2. Скоринг вакансии и сохранение в воронку CRM
python .agents/skills/job-search-agent/scripts/score_job.py "data/sample_vacancy.txt" --save-crm

# 3. Краткий отклик для hh.ru или развернутое письмо для HR
python .agents/skills/job-search-agent/scripts/generate_cover_letter.py "data/sample_vacancy.txt"
python .agents/skills/job-search-agent/scripts/generate_cover_letter.py "data/sample_vacancy.txt" --detailed

# 4. Подготовка к интервью в 3 блока (STAR + Tech)
python .agents/skills/job-search-agent/scripts/prepare_interview.py "data/sample_vacancy.txt"

# 5. Разбор вопросов прошедшего собеседования
python .agents/skills/job-search-agent/scripts/interview_debrief.py "Спросили про уровни изоляции транзакций в PostgreSQL"

# 6. Просмотр воронки откликов CRM
python .agents/skills/job-search-agent/scripts/crm_pipeline.py --stats
```

---

## 📊 Методология скоринга SuperJob Pro (0–100)

- **Hard Skills Match (до 40 баллов)**: Python, FastAPI/Django, PostgreSQL, SQL, Linux, Git.
- **Experience & Grade (до 25 баллов)**: Trainee/Intern (25б), Junior (22–25б), Middle (0–5б).
- **Education & Domain (до 15 баллов)**: профильное СПО МТИ «Информационные системы».
- **Conditions & Transparency (до 10 баллов)**: 100% удаленка (Remote РФ), прозрачная вилка.
- **Red Flags Penalties (до -25 баллов)**: «10 ролей в одном» (-10б), токсичность (-10б), размытое ТЗ (-5б).

### Градация:
- 🔥 **HIGH FIT (80–100)**: приоритетный отклик в первые 2 часа.
- ⚡ **MEDIUM FIT (60–79)**: качественная вакансия с закрытием 1-2 гэпов.
- ⚠️ **LOW FIT (<60)**: отклик не рекомендуется.
