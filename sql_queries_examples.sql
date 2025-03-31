-- выбрать всех сотрудников, текущая должность которых «Менеджер по продажам», и у которых есть предыдущая должность (то есть они уже повышались/переводились).
SELECT employee_id, last_name, first_name, cur_position, prev_position, current_salary FROM Employee
 WHERE cur_position = 'Менеджер по продажам'
   AND prev_position IS NOT NULL;

-- вывести всех сотрудников, отсортировав сначала по текущей должности (по алфавиту), а внутри — по убыванию зарплаты.
SELECT employee_id, last_name, first_name, cur_position, current_salary FROM Employee
 ORDER BY cur_position ASC, current_salary DESC;

-- посмотреть, сколько сотрудников в каждой текущей должности, и вывести только те должности, в которых больше одного сотрудника.
SELECT cur_position, COUNT(*) AS cnt FROM Employee
 GROUP BY cur_position
HAVING COUNT(*) > 1;

-- получить список заказов, сделанных в марте 2023 года, с ФИО и текущей должностью сотрудника, оформившего заказ
SELECT o.order_id, o.order_date, e.last_name || ' ' || e.first_name AS employee_fullname, e.cur_position AS employee_position, o.total_amount
  FROM "Order" o JOIN Employee e ON o.employee_id = e.employee_id
 WHERE o.order_date >= '2023-03-01'
   AND o.order_date <  '2023-04-01';

-- посмотреть, есть ли у заказов двигатели, и вывести все заказы. Если в заказе не было куплено двигателей, то Order_Engine.engine_id будет NULL.
SELECT o.order_id, o.order_date, oe.engine_id, oe.quantity
  FROM "Order" o LEFT JOIN Order_уngine oe
    ON o.order_id = oe.order_id
 ORDER BY o.order_id;

-- вывести каждого сотрудника и количество заказов, которые он оформил.
SELECT e.employee_id, e.last_name || ' ' || e.first_name AS employee_fullname, e.cur_position,
       (
         SELECT COUNT(*)
           FROM "Order" o
          WHERE o.employee_id = e.employee_id
       ) AS order_count
  FROM Employee e;

-- найти заказы, в которых присутствуют какие-либо товары категории «расходники» марки «Bosch». Для этого смотрим в таблицу Order_Consumable, связав её с Consumable по consumable_id.
SELECT o.order_id, o.order_date, o.total_amount FROM "Order" o
 WHERE o.order_id IN (
       SELECT oc.order_id
         FROM Order_сonsumable oc
         JOIN Consumable c ON oc.consumable_id = c.consumable_id
        WHERE c.brand = 'Bosch'
      );

-- ранжировать сотрудников по их зарплате (вывести их ФИО, текущую должность, зарплату и ранг).
SELECT employee_id, last_name, first_name, cur_position, current_salary, RANK() OVER (ORDER BY current_salary DESC) AS sal_rank
  FROM Employee;

-- получить для каждого сотрудника накопленную сумму (running total) оформленных заказов по хронологии.
SELECT o.employee_id, e.last_name, e.first_name, e.cur_position, o.order_date, o.total_amount,
       SUM(o.total_amount) OVER (
         PARTITION BY o.employee_id
         ORDER BY o.order_date
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS cume_total
  FROM "Order" o
  JOIN Employee e ON e.employee_id = o.employee_id
 ORDER BY o.employee_id, o.order_date;

-- найти топ‑3 сотрудников (по зарплате), пропустив первую запись (OFFSET1). Получаем двух «серебряных» и «бронзовых» сотрудников по уровню зарплаты.
SELECT employee_id, last_name, first_name, cur_position, current_salary
  FROM Employee
 ORDER BY current_salary DESC
 LIMIT 3
OFFSET 1;
