import json

from toolbox.utilities import execute_sql_query

if __name__ == "__main__":
    sql_query = """
SELECT CASE counts.region
           WHEN 'E' THEN 'England'
           WHEN 'W' THEN 'Wales'
           WHEN 'N' THEN 'Northern Ireland'
           ELSE 'Unknown Region: ' || counts.region END,
       counts.region_count
FROM (SELECT LEFT(region, 1) AS region, COUNT(*) AS region_count
      FROM casev2.cases
      WHERE receipt_received = true
        AND action_plan_id = '432f0597-0076-4adb-834b-bf249dc06ded'
      GROUP BY LEFT(region, 1)) AS counts
    """

    db_result = execute_sql_query(sql_query)

    regional_counts = dict(db_result)
    regional_counts['Total'] = sum(regional_counts.values())
    print(json.dumps(regional_counts))
