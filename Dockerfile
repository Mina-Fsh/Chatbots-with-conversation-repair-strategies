FROM rasa/rasa-sdk:2.2.0

COPY actions /app/actions

USER root
RUN pip install --no-cache-dir -r /app/actions/requirements-actions.txt
RUN python -m spacy download en_core_web_sm en

USER 1001
CMD ["start", "--actions", "actions", "-p", "5056", "--debug"]