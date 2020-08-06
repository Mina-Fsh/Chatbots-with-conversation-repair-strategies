FROM rasa/rasa-sdk:1.10.2

COPY actions /app/actions

USER root
RUN pip install --no-cache-dir -r /app/actions/requirements-actions.txt

# Download spacy language data
RUN python -m spacy download en_core_web_md
RUN python -m spacy link en_core_web_md en

USER 1001
CMD ["start", "--actions", "actions", "--debug"]

