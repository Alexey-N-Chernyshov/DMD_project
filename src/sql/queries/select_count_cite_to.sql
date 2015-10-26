SELECT 
   article.paper_title, cite.to_id, count(*)
FROM 
  article,
  cite
WHERE 
  article.id = cite.to_id
GROUP BY cite.to_id, article.paper_title
ORDER BY
  count(*) DESC