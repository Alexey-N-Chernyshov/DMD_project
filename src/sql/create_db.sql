CREATE TABLE article
(
  id INTEGER,
  paper_title TEXT NOT NULL,
  year INTEGER,
  venue TEXT,
  CONSTRAINT article_id PRIMARY KEY (id)
);

CREATE TABLE author
(
  id INTEGER NOT NULL,
  name TEXT NOT NULL,
  institute TEXT,
  CONSTRAINT author_id PRIMARY KEY (id)
);

CREATE TABLE article_author
(
  article_id INTEGER,
  author_id INTEGER,
  FOREIGN KEY (article_id) REFERENCES article (id),
  FOREIGN KEY (author_id) REFERENCES author (id),
  CONSTRAINT uc_article_author PRIMARY KEY (article_id, author_id)
);

CREATE TABLE keyword
(
  id INTEGER,
  tag TEXT NOT NULL,
  CONSTRAINT pk_keyword PRIMARY KEY (id)
);

CREATE TABLE article_keyword
(
  article_id INTEGER,
  keyword_id INTEGER,
  FOREIGN KEY (article_id) REFERENCES article (id),
  FOREIGN KEY (keyword_id) REFERENCES keyword (id),
  CONSTRAINT uc_article_keyword PRIMARY KEY (article_id, keyword_id)
);

CREATE TABLE cite
(
  id_from INTEGER,
  id_to INTEGER,
  FOREIGN KEY (id_from) REFERENCES article (id),
  FOREIGN KEY (id_to) REFERENCES article (id),
  CONSTRAINT uc_article_cite PRIMARY KEY (id_from, id_to)
);
