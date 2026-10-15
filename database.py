import sqlite3
from config import DATABASE

def get_db_connection():
    """Repeatable connector to db"""
    return sqlite3.connect(DATABASE)

def get_sked_by_day(day, site):
    """Get list of potential attendee of a site by day

        Args:
            Weekday: Shorted weekday name such as "Tues" for Tuesday
            Site shortcode: example: 'TG' for Tacoma General

        Returns: data from the roster in WHOTHEFUCKKNOWS format
            
    """

    conn = get_db_connection()
    daily_sked = conn.execute(''' 
        select name
        from schedule
        join sites
        on schedule.SITE_ID = sites.id
        join initials
        on schedule.INITIALS_ID = initials.id
        where workday=? and sites.code=?;''', (day, site)).fetchall()

    conn.close()

    return daily_sked

def get_site_list():
    """
    Get a list of the current jobsites

    Args:
    None

    Returns: data from the db containing a list of sites

    """
    conn = get_db_connection()
    site_list = conn.execute('''
        SELECT site_name from sites
    ''').fetchall()

    conn.close()

    return site_list

def get_roster():
    """
    Returns a list of all the current jobsite attendees
    :return:
    """
    conn = get_db_connection()
    roster = conn.execute('''
        SELECT name from initials
    ''').fetchall()

    conn.close()

    return roster

def add_site(code, name):
    """
    Adds a new jobsite
    Args:
    code: shortcode for jobsite
    name: Long name of jobsite
    :return:
    """
    conn = get_db_connection()

    cursor = conn.execute('''
        SELECT * 
        FROM sites
        where code=?;''', (code,)).fetchall()

    if len(cursor) == 0:
        conn.execute('''
                          INSERT into sites (CODE, SITE_NAME)
                          VALUES (?, ?)
                          ''', (code, name))
        conn.commit()
    else:
        print("Duplicate site!")

    conn.close()
    return None

def remove_site(code, site_name):
    """Removes site from list
    must have both site_name and shortcode to prevent accidental deletion of other sites"""
    conn = get_db_connection()
    conn.execute('''
        DELETE from sites 
        where code=? and site_name=?''', (code, site_name))
    conn.commit()
    conn.close()

    return None

def add_initials(initials):
    """
    Adds participants initials to roster

    :param initials:
    :return:
    """

    conn = get_db_connection()
    conn.execute("""
            INSERT into initials (name)
            values (?)
            """, (initials,))
    conn.commit()
    conn.close()

    return None

def remove_initials(initials):
    """
    Removes participants initials from roster. Used only for leavers
    :param initials:
    :return:
    """
    conn = get_db_connection()
    conn.execute('''
    DELETE from initials 
    where name=?''', (initials,))
    conn.commit()
    conn.close()

#add_to_sked


#remove_from_sked