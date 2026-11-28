-- =====================================================================
-- Capstone Project: Tata Play Subscriber Retention & Support Copilot
-- =====================================================================

-- =====================================================================
-- queries.sql  --  Part-A, Step-3: Four SQL queries on data/tataplay.db
-- Tables : subscribers, recharges, plans
-- Rule   : Only SUCCESSFUL Recharges are used unless a Task says otherwise.
-- Format : Each query starts with a marker line of the form "-- Q1 ..."
--          so that a3_run_queries.py can split the file into queries.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Q1 --> Revenue by Plan
-- INNER JOIN keeps only Rows that match in all Three tables.
-- ---------------------------------------------------------------------
SELECT p.plan_name,
       SUM(r.amount_inr)               AS revenue,
       ROUND(AVG(r.amount_inr), 2)     AS avg_amount,
       COUNT(DISTINCT s.subscriber_id) AS n_subscribers
FROM recharges r
INNER JOIN subscribers s ON r.subscriber_id = s.subscriber_id
INNER JOIN plans p       ON s.plan_id = p.plan_id
WHERE r.status = 'success'
GROUP BY p.plan_name
ORDER BY revenue DESC;

-- ---------------------------------------------------------------------------
-- Q2 --> Subscribers who never Successfully recharged
-- LEFT JOIN keeps every subscriber; where no Successful Recharge matches,
-- The Recharge Columns are NULL. The Status filter sits in the ON clause
-- (not WHERE), Otherwise the NULL Rows we are looking for would be removed.
-- ---------------------------------------------------------------------------
SELECT s.subscriber_id, s.tenure_months
FROM subscribers s
LEFT JOIN recharges r
       ON r.subscriber_id = s.subscriber_id
      AND r.status = 'success'
WHERE r.recharge_id IS NULL;

-- --------------------------------------------------------------------------
-- Q3 --> Ranking of Subscribers within a City by Total Successful Recharges
-- Step-1 (CTE "totals"): Total per Subscriber.
-- Step-2: Three Window Functions side by side, restarting for each City.
-- --------------------------------------------------------------------------
WITH totals AS (
    SELECT s.subscriber_id, s.city, SUM(r.amount_inr) AS total
    FROM subscribers s
    INNER JOIN recharges r ON r.subscriber_id = s.subscriber_id
    WHERE r.status = 'success'
    GROUP BY s.subscriber_id, s.city
)
SELECT subscriber_id, city, total,
       RANK()       OVER (PARTITION BY city ORDER BY total DESC) AS rnk,
       DENSE_RANK() OVER (PARTITION BY city ORDER BY total DESC) AS dense_rnk,
       ROW_NUMBER() OVER (PARTITION BY city
                          ORDER BY total DESC, subscriber_id)    AS row_num
FROM totals
ORDER BY city, total DESC, subscriber_id;

-- ---------------------------------------------------------------------------------
-- Q4 --> Running Total of Successful Recharges for Subscriber TP00010
-- SUM(...) OVER (ORDER BY ...) adds up the Amounts Row by row, in Date order.
-- ---------------------------------------------------------------------------------
SELECT recharge_id, recharge_date, amount_inr,
       SUM(amount_inr) OVER (ORDER BY recharge_date, recharge_id) AS running_total
FROM recharges
WHERE subscriber_id = 'TP00010'
  AND status = 'success'
ORDER BY recharge_date, recharge_id;