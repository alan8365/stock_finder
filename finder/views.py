from django.shortcuts import render
from django.db import connection
from .models import Foreign, Investment


# Create your views here.
def index(request):
    template = 'index.html'

    with connection.cursor() as c:
        sql = '''
            SELECT fi.number, fi.name, ff.diff, fi.diff, fi.diff + ff.diff
            FROM finder_investment as fi
                     INNER JOIN finder_foreign ff ON fi.number = ff.number
            WHERE fi.number IN
                  (SELECT number
                   FROM finder_foreign
                   WHERE diff > 0
                     AND datetime =
                         (SELECT max(datetime) FROM finder_foreign)
                   INTERSECT
                   SELECT number
                   FROM finder_investment
                   WHERE diff > 0
                     AND datetime =
                         (SELECT max(datetime) FROM finder_investment))
        '''

        c.execute(sql)
        buy_latest_data = c.fetchall()

        sql = '''
            SELECT fi.number, fi.name, ff.diff, fi.diff, fi.diff + ff.diff
            FROM finder_investment as fi
                     INNER JOIN finder_foreign ff ON fi.number = ff.number
            WHERE fi.number IN
                  (SELECT number
                   FROM finder_foreign
                   WHERE diff < 0
                     AND datetime =
                         (SELECT max(datetime) FROM finder_foreign)
                   INTERSECT
                   SELECT number
                   FROM finder_investment
                   WHERE diff < 0
                     AND datetime =
                         (SELECT max(datetime) FROM finder_investment))
        '''

        c.execute(sql)
        sell_latest_data = c.fetchall()

    return render(request, template, {
        'buy': buy_latest_data,
        'sell': sell_latest_data
    })


def custom(request):
    template = 'custom.html'

    if request.method == 'GET':
        day = request.GET['day']
        count = request.GET['count']

        with connection.cursor() as c:
            sql = f'''
                SELECT ff.number, ff.name, count(ff.number)
                FROM finder_investment fi
                         join finder_foreign ff on fi.number = ff.number and fi.datetime = ff.datetime
                WHERE fi.id IN
                      (SELECT id
                       FROM finder_investment
                       WHERE diff > 0
                         AND datetime IN
                             (SELECT datetime
                              FROM finder_investment
                              GROUP BY datetime
                              ORDER BY datetime DESC
                              LIMIT {day}
                             )
                      )
                  and ff.id IN
                      (SELECT id
                       FROM finder_foreign
                       WHERE diff > 0
                         AND datetime IN
                             (SELECT datetime
                              FROM finder_foreign
                              GROUP BY datetime
                              ORDER BY datetime DESC
                              LIMIT {day}
                             )
                      )
                GROUP BY ff.number
                HAVING count(ff.number) >= {count}
            '''

            c.execute(sql)
            buy_latest_data = c.fetchall()

            sql = f'''
                SELECT ff.number, ff.name, count(ff.number)
                FROM finder_investment fi
                         join finder_foreign ff on fi.number = ff.number and fi.datetime = ff.datetime
                WHERE fi.id IN
                      (SELECT id
                       FROM finder_investment
                       WHERE diff < 0
                         AND datetime IN
                             (SELECT datetime
                              FROM finder_investment
                              GROUP BY datetime
                              ORDER BY datetime DESC
                              LIMIT {day}
                             )
                      )
                  and ff.id IN
                      (SELECT id
                       FROM finder_foreign
                       WHERE diff < 0
                         AND datetime IN
                             (SELECT datetime
                              FROM finder_foreign
                              GROUP BY datetime
                              ORDER BY datetime DESC
                              LIMIT {day}
                             )
                      )
                GROUP BY ff.number
                HAVING count(ff.number) >= {count}
                    '''

            c.execute(sql)
            sell_latest_data = c.fetchall()

            # detail
            sql = f'''
                SELECT ff.datetime, ff.number, ff.name, ff.diff, fi.diff
                FROM finder_investment as fi
                         INNER JOIN finder_foreign ff ON fi.number = ff.number and fi.datetime = ff.datetime
                WHERE ff.number IN
                      (SELECT number
                       FROM finder_investment
                       WHERE diff > 0
                         AND datetime IN
                             (SELECT datetime
                              FROM finder_investment
                              GROUP BY datetime
                              ORDER BY datetime DESC
                              LIMIT {day})
                       GROUP BY number
                       HAVING count(number) = {count}
                       INTERSECT
                       SELECT number
                       FROM finder_foreign
                       WHERE diff > 0
                         AND datetime IN
                             (SELECT datetime
                              FROM finder_foreign
                              GROUP BY datetime
                              ORDER BY datetime DESC
                              LIMIT {day})
                       GROUP BY number
                       HAVING count(number) = {count})
            '''

            c.execute(sql)
            buy_detail = c.fetchall()

            sql = f'''
                SELECT ff.datetime, ff.number, ff.name, ff.diff, fi.diff
                FROM finder_investment as fi
                         INNER JOIN finder_foreign ff ON fi.number = ff.number and fi.datetime = ff.datetime
                WHERE ff.number IN
                      (SELECT number
                       FROM finder_investment
                       WHERE diff < 0
                         AND datetime IN
                             (SELECT datetime
                              FROM finder_investment
                              GROUP BY datetime
                              ORDER BY datetime DESC
                              LIMIT {day})
                       GROUP BY number
                       HAVING count(number) = {count}
                       INTERSECT
                       SELECT number
                       FROM finder_foreign
                       WHERE diff < 0
                         AND datetime IN
                             (SELECT datetime
                              FROM finder_foreign
                              GROUP BY datetime
                              ORDER BY datetime DESC
                              LIMIT {day})
                       GROUP BY number
                       HAVING count(number) = {count})
                    '''

            c.execute(sql)
            sell_detail = c.fetchall()

        return render(request, template, {
            'buy': buy_latest_data,
            'sell': sell_latest_data,
            'detail': buy_detail + sell_detail,
        })
