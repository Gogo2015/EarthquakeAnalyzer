FROM python:3.12

WORKDIR /code

# Copy requirements first
COPY requirements.txt .

# Install dependencies from requirements.txt
RUN pip3 install -r requirements.txt

# Copy the rest of the application
COPY src/api.py src/jobs.py src/worker.py ./

# Copy test files
COPY test/test_api.py test/test_worker.py ./test/

RUN chmod +rx api.py jobs.py worker.py test/test_api.py test/test_worker.py

ENV PATH="/code:$PATH"

ENTRYPOINT [ "python" ]
CMD [ "api.py" ]