import sqlite3


class Table:
    def __init__(self, table, columns: tuple):
        self.conn = sqlite3.connect('data.db')
        self.c = self.conn.cursor()
        self.table = table
        self.columns = columns

    def get(self, id_str, columns: str='*'):
        self.c.execute("SELECT {0} FROM {1} WHERE id=:id".format(columns, self.table), {'id': id_str})
        return self.c.fetchone()

    def get_all(self, columns: str='*'):
        self.c.execute("SELECT {0} FROM {1}".format(columns, self.table))
        return self.c.fetchall()

    def add_element(self, id_str, values: dict=None):
        if values is None:
            values = {}

        values['id'] = id_str

        for column in self.columns:
            if column not in values:
                values[column] = 0  # sets default value 0

        with self.conn:
            self.c.execute(
                "INSERT INTO {0} VALUES {1}".format(
                    self.table,
                    tuple(map(lambda col: ':' + col, self.columns))
                ).replace("'", ''),
                values
            )
        return values

    def update(self, id_str, values: dict):
        values['id'] = id_str

        with self.conn:
            self.c.execute(
                "UPDATE {0} SET {1} WHERE id=:id".format(
                    self.table,
                    tuple(map(lambda col: col + ' = :' + col, values))
                ).replace("'", '').replace('(', '').replace(')', ''),
                values
            )
        return values

    def add_to_value(self, id_str, column: str, val_to_add):
        current = self.get(id_str, column)[0]
        new = current + val_to_add
        with self.conn:
            self.update(id_str, {column: new})

        return new

    def sort(self, column: str):
        data_list = self.get_all('id, ' + column)
        data_list.sort(key=lambda element: element[1], reverse=True)

        return data_list


tickets = Table('tickets', ('id', 'author', 'server', 'info', 'added', 'closed'))
servers = Table('servers', ('id', 'prefix', 'channel', 'role'))
