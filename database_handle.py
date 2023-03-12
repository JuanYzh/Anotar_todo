# -*- coding: utf-8 -*-
# Copyright (c) 2023 by wen-Huan.
# Date: 2023-03.01
# Ich und google :)
import sqlite3
import hashlib
import os


class FileDatabase:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_table()

    def __del__(self):
        self.conn.close()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                display TEXT,
                md5 TEXT UNIQUE,
                uuid TEXT UNIQUE,
                path TEXT UNIQUE,
                note TEXT,
                show TEXT
            )
        ''')
        self.conn.commit()

    def add_file(self, display, md5, uuid, path, note, show):
        self.cursor.execute('''
            INSERT OR REPLACE INTO files (display, md5, uuid, path, note, show)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (display, md5, uuid, path, note, show))
        self.conn.commit()

    def update_file(self, md5="", uuid="", path="", note="", show="T"):
        if path:
            display_name = os.path.basename(path)
        else:
            display_name = ""
        result = self.find_file(md5, uuid, path)
        if result:
            id, old_display, old_md5, old_uuid, old_path, old_note, old_show = result
            self.cursor.execute('''
                UPDATE files
                SET display=?, md5=?, uuid=?, path=?, note=?, show=?
                WHERE id=?
            ''', (display_name, md5, uuid, path, note, show, id))
            self.conn.commit()
            return old_note
        else:
            self.add_file(display_name, md5, uuid, path, note, show)

    def find_file(self, md5=None, uuid=None, path=None):
        if md5:
            self.cursor.execute('SELECT * FROM files WHERE md5=?', (md5,))
            result = self.cursor.fetchone()
            if result:
                return result

        if uuid:
            self.cursor.execute('SELECT * FROM files WHERE uuid=?', (uuid,))
            result = self.cursor.fetchone()
            if result:
                return result

        if path:
            self.cursor.execute('SELECT * FROM files WHERE path=?', (path,))
            result = self.cursor.fetchone()
            if result:
                return result

        return None

    def read_db_to_dict(self):
        c = self.cursor
        c.execute("SELECT * FROM files")
        rows = c.fetchall()
        file_dict = {}
        for row in rows:
            if row[6] == "T":
                file_dict[row[4]] = {"display":row[1], "md5": row[2], "uuid": row[3], "path": row[4], "note": row[5]}
        return file_dict

    def close_db(self):
        self.conn.close()

if __name__ == '__main__':
    db = FileDatabase('file.db')
    if not os.path.exists("file.db"):
        md5 = hashlib.md5('test'.encode('utf-8')).hexdigest()
        uuid = '12345'
        path = '/path/to/file'
        note = 'This is a test file'
        db.add_file(md5, uuid, path, note)

    new_md5 = hashlib.md5('t451t'.encode('utf-8')).hexdigest()
    new_uuid = '67945'
    new_path = '/new/paath/to/fi2e'
    new_note = 'This is a newe22yy TEST'
    old_note = db.update_file(new_md5, new_uuid, new_path, new_note)
    print('Old note:', old_note)

    dic = db.read_db_to_dict()
    print(dic)
