# Patient Health Records (Flask + SQLite + AI)

CRUD app for patient blood-test records. After a record is saved, an AI model
predicts a possible health condition and the result is stored in **Remarks**.

## Stack
- Backend: Python, Flask, SQLite
- Frontend: Jinja templates + Bootstrap 5
- AI: Anthropic Messages API (falls back to a labelled rule-based remark if no key/API error)

## Run
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key      # Windows PowerShell: $env:ANTHROPIC_API_KEY="your-key"
python app.py                          # open http://127.0.0.1:5000
```

## Structure
- `app.py` - routes (create, read, update, delete, `/api/patients` JSON)
- `validators.py` - name, dd/mm/yyyy date, email, numeric range checks
- `ai_service.py` - AI API call and fallback
- `run_test_data.py` - submits the 10 assessment records and prints results

## Validation rules
- Name: letters, spaces, `. ' -`
- DOB: dd/mm/yyyy (dd.mm.yyyy and dd-mm-yyyy also accepted and normalised), real date, not in the future
- Email: valid format and unique
- Glucose 20-600, Haemoglobin 3-25, Cholesterol 50-600 (numeric)

Not medical advice.
