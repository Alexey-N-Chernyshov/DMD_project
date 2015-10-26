SELECT * FROM article, article_keyword, keyword
WHERE keyword.tag = 'Wonderland'
AND keyword.id = article_keyword.keyword_id
AND article_keyword.article_id = article.id;
