SELECT 
  article.paper_title
FROM 
  public.article, 
  public.cite
WHERE 
  article.id = cite.from_id AND
  cite.to_id = (
SELECT
  article.id
FROM
  article
WHERE
  article.paper_title = 'Fundamentals of Database Systems, 2nd Edition.'  
)
ORDER BY
  paper_title