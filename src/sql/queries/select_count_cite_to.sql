SELECT 
   article.paper_title, reference.to_id, count(*)
FROM 
  article,
  reference
WHERE 
  article.id = reference.to_id
GROUP BY reference.to_id, article.paper_title
ORDER BY count(*) DESC