FROM python:3.12-slim

# Creates application directory
WORKDIR /app

# Creates an appuser and change the ownership of the application's folder
RUN useradd appuser && chown appuser ./

# Installs pip
RUN pip install --upgrade pip

# Copies requirements
COPY --chown=appuser ./requirements.txt ./

# Installs projects dependencies
RUN pip install -r requirements.txt

COPY --chown=appuser . ./
