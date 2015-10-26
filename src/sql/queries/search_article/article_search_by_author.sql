SELECT * FROM article, author, article_author
WHERE author.name = 'Lewis Carroll'
AND author.id = article_author.author_id
AND article_author.article_id = article.id;
