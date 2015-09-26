SELECT * FROM article, author, article_author
WHERE author.institute = 'Oxford'
AND author.id = article_author.author_id
AND article_author.article_id = article.id;
