FROM continuumio/miniconda3 as base

LABEL maintainer="Korbit ML Apps"
LABEL description="Template for ML apps"

# Directory Creation
ENV APP_ROOT /opt/korbit
RUN mkdir $APP_ROOT && \
    mkdir /etc/korbit
WORKDIR $APP_ROOT


FROM base as requirements
COPY ./environment.yml $APP_ROOT/

RUN conda env create --quiet --force environment.yml
RUN conda clean --quiet --all --yes
SHELL ["conda", "run", "-n", "social-response-classifier", "/bin/bash", "-c"]

FROM requirements as container
COPY . .
RUN chmod +x entrypoint.sh

EXPOSE $APP_EXPOSED_PORT
ENV FLASK_DEBUG 1
CMD ["./entrypoint.sh"]