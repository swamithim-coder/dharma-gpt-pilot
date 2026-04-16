# Dharma GPT Pilot - Streamlit Community Cloud Prep

## Files
- app.py
- backend_pipeline.py
- ingest_first_records.py
- requirements.txt
- .gitignore

## Deployment steps
1. Put your project files in a GitHub repository.
2. Make sure requirements.txt is in the repo root.
3. Go to Streamlit Community Cloud and deploy from the GitHub repo.
4. Choose app.py as the entrypoint.
5. In app settings / secrets, add:
   - OPENAI_API_KEY
   - QDRANT_URL
   - QDRANT_API_KEY