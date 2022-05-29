# import libraries
import sqlite3
from time import time
from pandas import DataFrame
from datetime import datetime
import nltk
import re


def create_table(table: str, field: dict) -> None:
    field = ",".join([f"{k} {v}" for k,v in field.items()])
    with sqlite3.connect("data/barkas.db") as con:
        cur = con.cursor()
        cur.execute(f"CREATE TABLE {table} ({field});")
        con.commit()

def clear(table: str = "posts") -> None:
    with sqlite3.connect("data/barkas.db") as con:
        cur = con.cursor()
        cur.execute(f"DELETE FROM {table};")

def insert(entry: dict, table: str = "posts") -> None:
    n = len(entry)
    values = list(entry.values())
    keys = ",".join(list(entry.keys()))
    with sqlite3.connect("data/barkas.db") as con:
        cur = con.cursor()
        cmd = f"""INSERT or IGNORE INTO {table} ({keys}) VALUES({",".join(["?" for _ in range(n)])})"""
        cur.execute(cmd,(*values,))
        con.commit()

def query_all(columns: list, exclude_none: str = "caption", table: str = "posts") -> list:
    with sqlite3.connect("data/barkas.db") as con:
        cur = con.cursor()
        cur.execute(f"SELECT {','.join(columns)} FROM {table} WHERE {exclude_none} IS NOT NULL;")
        data = DataFrame(cur.fetchall(),columns=columns)
    return data

def update_label(shortcode: str, label: str, table: str = "posts") -> None:
    with sqlite3.connect("data/barkas.db") as con:
        cur = con.cursor()
        cur.execute(f"UPDATE {table} SET label=? WHERE shortcode=?",(label,shortcode))
        con.commit()

def update_timestamp(shortcode: str, post_date: int, table: str = "posts") -> None:
    date = datetime.strptime(post_date,"%H:%M:%S %d %b %Y")
    timestamp = int(date.timestamp())
    with sqlite3.connect("data/barkas.db") as con:
        cur = con.cursor()
        cur.execute(f"UPDATE {table} SET timestamp=? WHERE shortcode=?",(timestamp,shortcode))
        con.commit()

def update(entry: dict, table: str = "posts") -> None:
    shortcode = entry['shortcode']
    entry.pop('shortcode')
    values = [*entry.values()]
    with sqlite3.connect("data/barkas.db") as con:
        cur = con.cursor()
        cur.execute(f"UPDATE {table} SET {','.join([key+'=?' for key in entry.keys()])} WHERE shortcode=?",(*values,shortcode))
        con.commit()

def delete(shortcode: str, table: str = "posts") -> None:
    with sqlite3.connect("data/barkas.db") as con:
        cur = con.cursor()
        cur.execute(f"DELETE FROM {table} WHERE shortcode=?",(shortcode,))
        con.commit()

def text_preprocessing(data: DataFrame, column: str) -> DataFrame:
    nltk.download("stopwords")
    from nltk.corpus import stopwords

    def stopwords_removal(word):
        filtering = stopwords.words("indonesian","english")
        fit = list(filter(lambda x: False if x in filtering else True, word))
        return fit
    
    data[column] = data[column].apply(lambda caption: re.findall("\w+",caption.lower()))
    data[column] = data[column].apply(stopwords_removal)
    data[column] = data[column].apply(lambda words: " ".join(words))

    return data

if __name__ == "__main__":

    # Test: Create Table
    field = dict(
        shortcode="TEXT UNIQUE",
        timestamp="INT",
        latest_update="TEXT",
        post_date="TEXT",
        post_url="TEXT",
        thumbnail="TEXT",
        owner="TEXT",
        caption="TEXT",
        label="TEXT",
        likes="INT",
        comments="INT",
        mentioned="TEXT",
        tagged="TEXT",
        hashtags="TEXT",
        is_video="BOOL",
        type="TEXT"
    )
    create_table("posts")