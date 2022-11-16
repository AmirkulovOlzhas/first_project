import sqlite3
import sys
import traceback
import random


def scrub(table_name):
    return ''.join(chr for chr in table_name if chr.isalnum())


def read_sqlite_table(city1, city2, date):
    # Message_search_result все результаты поиска
    try:
        conn = sqlite3.connect(r'D:\Programs\PyCharm\ttstore\tt_store.db')
        cur = conn.cursor()
        name_of_table = []
        travel_index = []
        print("Подключен к SQLite для read_sqlite_table")

        cur.execute("""SELECT * FROM tablel""")
        records = cur.fetchall()
        if date != '':  # если дата указана
            for row in records:
                if str(row[1]) == city1:
                    if str(row[2]) == city2:
                        if str(row[3]) == date:
                            name_of_table.append(row[4])
                            travel_index.append(row[5])
        else:
            for row in records:
                if str(row[1]) == city1:
                    if str(row[2]) == city2:
                        name_of_table.append(row[4])
                        travel_index.append(row[5])

        return name_of_table, travel_index
        cur.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            cur.close()
            print("closed")


def select_place(table_name):
    try:
        conn = sqlite3.connect(r'D:\Programs\PyCharm\ttstore\tt_store.db')
        cur = conn.cursor()
        print("Подключен к SQLite для select_place")

        cur.execute("SELECT place FROM '%s'" % scrub(table_name))
        places = cur.fetchall()  # тут записи о месте
        cur.execute("SELECT status FROM '%s'" % scrub(table_name))
        statuses = cur.fetchall()  # статусе места
        return places, statuses
        cur.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite#2", error)
    finally:
        if conn:
            cur.close()
            print("closed")


def set_order(chose_place, client_name, table_index):
    try:
        conn = sqlite3.connect(r'D:\Programs\PyCharm\ttstore\tt_store.db')
        cur = conn.cursor()
        print("Подключен к SQLite для set_order")
        tname = '  ---' + table_index + ' - '

        cur.execute("SELECT place FROM '%s'" % table_index)
        nr_places = cur.fetchall()  # тут записи о месте
        cur.execute("SELECT status FROM '%s'" % table_index)
        nr_status = cur.fetchall()  # статусе места
        places = []
        status = []
        error_stat_1 = 0  # число ошибок, если выбранное место уже занято
        return_cods = []
        for i in nr_status:
            status.append(i[0])
        for i in nr_places:
            places.append(i[0])

        for row in chose_place:
            for k in places:
                if int(k) == int(row):
                    calc = 1  # будем считать до к
                    for row1 in status:
                        if k == calc:
                            if int(row1) == 1:
                                error_stat_1 += 1
                            break
                        calc += 1
        if error_stat_1 == 0:
            for row1 in chose_place:
                gen_code = random.randint(1000, 9999)
                return_cods.append(gen_code)
                cur.execute(
                    f"UPDATE " + scrub(
                        tname) + f" SET status = '%s',name = '%s', code = '%s' WHERE place = '%s'" % (
                        1, str(client_name), int(gen_code), int(row1)))
                conn.commit()
        return return_cods

    except Exception as e:
        print("Ошибка при работе с SQLite#3", e)
        for frame in traceback.extract_tb(sys.exc_info()[2]):
            fname, lineno, fn, text = frame
            print("Error in %s on line %d" % (fname, lineno))

