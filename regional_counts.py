from utilities.db_helper import execute_sql_query

if __name__ == "__main__":
    sql_query = """
SELECT CASE LEFT(region, 1)
           WHEN 'E' THEN 'England'
           WHEN 'W' THEN 'Wales'
           WHEN 'N' THEN 'Northern Ireland'
           ELSE region END AS region, COUNT(*)
FROM casev2.cases
WHERE receipt_received = true
AND action_plan_id = '432f0597-0076-4adb-834b-bf249dc06ded'
GROUP BY region;
        """

    db_result = execute_sql_query(sql_query)

    regional_counts = dict(db_result)
    regional_counts['Total'] = sum(regional_counts.values())
    print(regional_counts)
