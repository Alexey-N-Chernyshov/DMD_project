SELECT article.paper_title, SUM(cnt) AS auth_range
FROM
  article,
  article_author,
  (SELECT author.id, author.name, count(*) AS cnt
    FROM
      author,
      article_author,
      article,
      cite
    WHERE
      author.id = article_author.author_id AND
      article.id = article_author.article_id AND
      article.id = cite.to_id
    GROUP BY author.id
  ) AS auth
WHERE
  article_author.author_id = auth.id AND
  article.id = article_author.article_id 
GROUP BY article.paper_title, article.id
ORDER BY auth_range DESC
  