#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      wad9yok
#
# Created:     18/06/2013
# Copyright:   (c) wad9yok 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import praw
import re
from pprint import pprint
import sqlite3 as lite
from datetime import datetime
import pygal

def connect_to_trees():
    r = praw.Reddit(user_agent='HowHigh?Bot from /u/thelemonpress')
    return r

def get_posts( r, how_many ):
    posts = r.get_subreddit('trees+treesgonewild').get_hot(limit=how_many)
    return list(posts)

def get_all_comments( posts ):
    comments = []
    for p in posts:
        comments.append( p.title )
        print " >> " + (p.title)

        p.replace_more_comments(limit=None, threshold=0)
        flat_comments = praw.helpers.flatten_tree(p.comments)

        for c in list(flat_comments):
            if type(c) != praw.objects.MoreComments:
                comments.append(c.body)
    return comments

def get_numbers( comments ):
    matches = []
    pattern = r"\[(\d|1\d|a\s\d)\]"
    p = re.compile( pattern )

    for com in comments:
        scores = p.findall( com )
        for score in scores:
            result = int(score)
            if result <= 10:
                matches.append(result)
    return sorted( matches )

def make_histogram( results ):
    hist_dict = {}
    for i in range(11):
        hist_dict[i] = 0
    for r in results:
            hist_dict[r] = hist_dict[r] + 1
    return hist_dict

def hist_to_string( hist ):
    result = ""
    for k, v in hist.iteritems():
        result = result + str(v) + " "
    return str(result)

def push_to_db( hist, date ):
    new_row = (str(date), hist)
    con = lite.connect(r'C:\B_Py\HH\hh.db')
    now = str(datetime.now())
    with con:
        cur = con.cursor()
        cur.execute("INSERT INTO hh(Date, Data) VALUES(?, ?)", new_row)
    return

def check_db_exists():
    return True

def create_db():
    print "DB needs creating. Doing it now..."
    con = lite.connect(r'C:\B_Py\HH\hh.db')
    with con:
        cur = con.cursor()
        cur.execute("CREATE TABLE hh (Id INTEGER PRIMARY KEY, Date TEXT, Data TEXT)")
    return

def get_now():
    return str( datetime.now()).split(".")[:-1]

def get_all_data():
    con = lite.connect(r'C:\B_Py\HH\hh.db')
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM hh")
        rows = cur.fetchall()
    return rows

def normalise( data ):
    new_data = []
    for row in data:
        new_row = []
        total = sum(row)
        factor = 100.0/total
        for i in row:
            new_num = i * factor
            new_row.append( float( float(i) * float(factor) ) )
        new_data.append(new_row)
    return new_data

def get_columns(matrix):
    columns = [[row[col] for row in matrix] for col in range(len(matrix[1]))]
    return columns

def convert_data( all_data ):
    nums_by_date = []
    for row in all_data:    #turn the row into a list of ints
        num_list = map( int, row[2][:-1].split(" ") )
        nums_by_date.append(num_list)
    norm_data = normalise( nums_by_date )   #normalise to 1000
    data = get_columns(norm_data)    #rotate matrix by 90deg
    return data

def get_dates( all_data ):
    dates = []
    for row in all_data:
        dates.append(str(row[1][2:-2]))
    return dates

def create_graph( all_data ):
    tree_colors = (
    '#00aa00', '#22aa00', '#44aa00',
    '#66aa00', '#88aa00', '#aaaa00', '#aa8800',
    '#aa6600', '#aa4400', '#aa2200', '#aa0000')

    TreeStyle = pygal.style.Style(
        background='#ffffaa',
        plot_background='#dddddd',
        foreground='#000000',
        foreground_light='#000000',
        foreground_dark='#000000',
        opacity='.75',
        opacity_hover='.9',
        transition='200ms ease-in',
        colors=tree_colors
        )

    data = convert_data( all_data )
    line_chart = pygal.StackedLine(fill=True, style=TreeStyle, x_label_rotation=20, interpolate='hermite')    #'lagrange'
    line_chart.title = 'How High Is R/Trees?'
    dates = get_dates(all_data)
    line_chart.x_labels = dates#map(str, range(0,len(all_data)))
    for i, d in enumerate(data):
        line_chart.add( str(i), d )
    line_chart.render_to_file('chart.svg')
    return



def main():
    if (not check_db_exists()):
        create_db()

    results =   get_numbers(
                get_all_comments(
                get_posts(
                connect_to_trees(), 100 ) ) )

    push_to_db( ( hist_to_string( make_histogram( results ) ) ),
               ( get_now() ) )

    create_graph( get_all_data() )
    pass

if __name__ == '__main__':
    main()




#{0: 5, 1: 1, 2: 1, 3: 1, 4: 3, 5: 3, 6: 9, 7: 16, 8: 4, 9: 2, 10: 5}   thurs afternoon hot
#{0: 3, 1: 1, 2: 1, 3: 3, 4: 1, 5: 2, 6: 11, 7: 15, 8: 8, 9: 4, 10: 3}  thurs night hot
#{0: 1, 1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 3, 7: 4, 8: 4, 9: 0, 10: 2}    thurs night new
#{0: 4, 1: 1, 2: 1, 3: 4, 4: 6, 5: 3, 6: 11, 7: 13, 8: 11, 9: 2, 10: 10}friday morn hot
#{0: 5, 1: 0, 2: 1, 3: 3, 4: 3, 5: 4, 6: 5, 7: 11, 8: 16, 9: 5, 10: 7}  saturday morn hot
#{0: 4, 1: 0, 2: 1, 3: 3, 4: 4, 5: 4, 6: 5, 7: 9, 8: 14, 9: 6, 10: 9}   saturday afternoon hot