SELECT author.name, count(*)
FROM
  author,
  article_author,
  article,
  cite
WHERE
  author.id = article_author.author_id AND
  article.id = article_author.article_id AND
  article.id = cite.to_id
GROUP BY author.name
ORDER BY count(*) DESC