FROM postgres:11

RUN apt-get update && apt-get install --no-install-recommends -y \
  wget \
  libpq-dev \
  python3 \
  python3-dev \
  python3-pip \
  python3-slugify \
  git \
  vim \
  && rm -rf /var/lib/apt/lists/*

COPY createInitDB.py ./
COPY setup.sh /docker-entrypoint-initdb.d/

RUN ln -s /docker-entrypoint-initdb.d/setup.sh setup.sh
