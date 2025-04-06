USE business_data;
SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='product_info'

SELECT[product_id], [name], [features], [price] FROM product_info

SELECT TOP 10 [product_id], [name], [price]
FROM (
  SELECT 
    [product_id], 
    [name], 
    CONVERT(MONEY, [price]) AS [price],
    ROW_NUMBER() OVER (ORDER BY CONVERT(MONEY, [price]) DESC) AS Row
  FROM [dbo].[product_info]
) AS subquery
WHERE Row <= 10