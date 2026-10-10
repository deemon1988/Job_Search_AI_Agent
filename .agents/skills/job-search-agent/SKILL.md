---
name: job-search-agent
description: >-
  Use this skill when searching for remote IT jobs, parsing vacancies from hh.ru, SuperJob, or Habr,
  evaluating and scoring jobs against the candidate profile (SuperJob Pro methodology 0-100),
  detecting employer red flags and toxicity, generating tailored cover letters using the 2-line Hook rule,
  preparing for 3-block interviews (Tech Screening + STAR behavioral + Questions for Employer),
  debriefing post-interview questions, or tracking applications in the SQLite CRM pipeline.
---

# Job Search Agent (SuperJob Pro Edition)

Персональный локальный AI-агент и экспертный скилл для поиска удалённой IT-работы, скоринга вакансий, генерации высококонверсионных откликов (3–5 в неделю), ведения CRM-воронки и подготовки к техническим и STAR-интервью.

База знаний и регламенты построены на рекомендациях портала работодателей и рекрутеров [SuperJob Pro](https://www.superjob.ru/pro/).

---

## Профиль кандидата (Дмитрий Турейко)
При любой генерации откликов, резюме и анализе вакансий опираться на проверенные факты:
- **Образование**: Среднее профессиональное образование (СПО) ОАНО ВО МТИ, специальность «Информационные системы (по отраслям)».
- **Ключевой стек**: Python (FastAPI, Django), PostgreSQL, SQL, Linux (Ubuntu), Nginx, Git, JavaScript, REST API.
- **Live-проекты**:
  - Production-сервис: [https://gorizont-blog.ru](https://gorizont-blog.ru) (деплой на Linux, Nginx, SSL).
  - GitHub: [https://github.com/deemon1988](https://github.com/deemon1988)
  - Проекты: `clinic_connect` (FastAPI/БД), `AI Blog Generator`, `Job Search AI Agent`.
- **Ограничения**: Строго **100% удалённая работа** (Remote РФ) из Ленинградской области (г. Сосновый Бор). Без гибрида и обязательных поездок в офис.
- **Зарплатные ориентиры**: 50 000 – 60 000 ₽ (Full-time), 25 000 – 35 000 ₽ (Part-time), «Не указана» (Стажировки).
- Подробнее: см. [candidate_profile.md](./references/candidate_profile.md).

---

## 🛠 Автономные инструменты и скрипты

Агент может выполнять операции через прямые скрипты в папке `scripts/`:

Команда / Скрипт | Назначение | Пример вызова
:---|:---|:---
`scripts/search_jobs.py` | Мультипоиск по hh.ru, Habr, ТрудВсем и стажировкам | `python .agents/skills/job-search-agent/scripts/search_jobs.py "Python стажер" --limit 5`
`scripts/parse_job.py` | Парсинг вакансии по URL или тексту | `python .agents/skills/job-search-agent/scripts/parse_job.py "https://hh.ru/vacancy/123456"`
`scripts/score_job.py` | Скоринг 0–100 по SuperJob Pro и выявление ред-флагов | `python .agents/skills/job-search-agent/scripts/score_job.py "data/sample_vacancy.txt" --save-crm`
`scripts/generate_cover_letter.py` | Генерация отклика (правило 2 строк) | `python .agents/skills/job-search-agent/scripts/generate_cover_letter.py "data/sample_vacancy.txt" --detailed`
`scripts/prepare_interview.py` | 3 блока подготовки к собеседованию (STAR + Tech) | `python .agents/skills/job-search-agent/scripts/prepare_interview.py "data/sample_vacancy.txt"`
`scripts/interview_debrief.py` | Разбор вопросов после реального интервью | `python .agents/skills/job-search-agent/scripts/interview_debrief.py "Спросили про индексы PostgreSQL"`
`scripts/crm_pipeline.py` | Просмотр и обновление воронки откликов SQLite | `python .agents/skills/job-search-agent/scripts/crm_pipeline.py --stats`

*(Все скрипты поддерживают флаг `--json` для получения машиночитаемого структурированного вывода).*

---

## 📋 Рабочие регламенты агента

### 1. Поиск вакансий и стажировок
1. Запусти `scripts/search_jobs.py` с нужными ключевыми словами или используй встроенный API-поиск.
2. Проверь требования к локации (только Remote РФ). Отсекай вакансии с обязательным гибридом.
3. Проверь каталог корпоративных программ (Сбер, Т-Банк, ИнфоТеКС, Яндекс).

### 2. Экспертный скоринг по SuperJob Pro
Оценивай вакансию по шкале от 0 до 100 баллов:
- **Hard Skills (до 40 баллов)**: совпадение с Python, SQL, PostgreSQL, Linux, Git.
- **Опыт и грейд (до 25 баллов)**: Trainee/Intern — 25б, Junior (0-1 год) — 22-25б, Middle (3+ года) — 0-5б.
- **Образование (до 15 баллов)**: профильное СПО МТИ по информационным системам.
- **Условия (до 10 баллов)**: 100% удаленка (+10б), белая вилка.
- **Штрафы за Red Flags (до -25 баллов)**:
  - «10 ролей в одном» (-10б);
  - Токсичность («24/7», «ненормированный график», «семья») (-10б);
  - Размытые обязанности (-5б).
- **Вердикт**:
  - 🔥 **HIGH (80–100)**: приоритетный отклик в первые 2 часа.
  - ⚡ **MEDIUM (60–79)**: хороший вариант с точечным закрытием гэпов.
  - ⚠️ **LOW (<60)**: отклик не рекомендован.

### 3. Составление сопроводительного письма (Hook Rule)
- **Правило 2 строк (Hook)**: рекрутер сканирует текст 5–10 секунд. Первые две строки обязаны закрыть главный фильтр (роль + СПО МТИ + профильный стек).
- **Фактологические пруфы**: прямые ссылки на [gorizont-blog.ru](https://gorizont-blog.ru) и [GitHub](https://github.com/deemon1988).
- **Строгий запрет клише**: никаких «стрессоустойчивый», «легко обучаемый», «коммуникабельный».
- **Два формата**:
  - *Краткий* (500–750 знаков) — для формы отклика на hh.ru / SuperJob.
  - *Развернутый* (800–1100 знаков) — для письма HR/тимлиду на email или в Telegram.

### 4. 3-блочная подготовка к интервью
1. **Блок 1: Технический скрининг** (10 точечных вопросов по стеку вакансии с готовыми тезисами).
2. **Блок 2: Поведенческие вопросы по STAR** (Situation, Task, Action, Result):
   - 90-секундный Elevator Pitch;
   - Кейс сложного бага/задачи на примере gorizont-blog.ru или Nginx;
   - Аргументация зарплаты 50-60k по стандарту SuperJob Pro.
3. **Блок 3: Вопросы работодателю** (3–4 зрелых вопроса про онбординг, код-ревью и задачи).

---

## 📚 Справочные материалы
- [Профиль кандидата](./references/candidate_profile.md)
- [Методология SuperJob Pro](./references/superjob_pro_rules.md)
- [3 варианта резюме](./references/resume_variants.md)
- [Руководство по STAR-интервью](./references/star_framework.md)
