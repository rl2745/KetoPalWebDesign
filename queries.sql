SELECT pname FROM person WHERE weight > 200 AND wid IS NULL;

SELECT dname,SUM(calories) AS total_calories FROM (diet NATURAL JOIN consists_of NATURAL JOIN food) GROUP BY did
HAVING SUM(calories) IN (SELECT MAX(calorie_total) FROM (SELECT SUM(calories) AS calorie_total FROM (diet NATURAL JOIN consists_of NATURAL JOIN food) GROUP BY did) cals); 

SELECT * FROM (SELECT pname, wname, weight*cal_expend_total AS cal_expenditure FROM person NATURAL JOIN
(SELECT wid,wname,SUM(cal_expend_per_lb) AS cal_expend_total FROM (Workout_Program NATURAL JOIN uses NATURAL JOIN exercise) GROUP BY wid) cals) user_cals ORDER BY cal_expenditure DESC;