import sqlite3
from config import DATABASE

def get_db_connection() -> sqlite3.Connection:
    """Repeatable connector to db"""
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def get_sked_by_day(day: str, site: str) -> list[tuple[str, str]]:
    """Get list of potential attendee of a site by day"""

    conn = get_db_connection()
    try:
        daily_sked = conn.execute(''' 
        SELECT name FROM schedule
        JOIN sites
        ON schedule.site_id = sites.id
        JOIN initials
        ON schedule.initials_id = initials.id
        where workday=? and sites.code=?;''', (day, site)).fetchall()
    finally:
        conn.close()

    return daily_sked

def get_site_list()  -> list[tuple[str, str]]:
    """Get a list of the current jobsites"""
    conn = get_db_connection()
    try:
        site_list = conn.execute('''
        SELECT site_name, code from sites
    ''').fetchall()
    finally:
        conn.close()

    return site_list

def get_roster() -> list[tuple[str, str]]:
    """Returns a list of all the current jobsite attendees"""
    conn = get_db_connection()
    try:
        roster = conn.execute('''
            SELECT name FROM initials
            ORDER BY name ASC;
        ''').fetchall()
    finally:
        conn.close()

    return roster

def add_site(code: str, name: str) -> None:
    """Adds a new jobsite"""
    conn = get_db_connection()

    try:
        conn.execute('''
          INSERT into sites (CODE, SITE_NAME)
          VALUES (?, ?)
          ''', (code, name))
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

    return None

def remove_site(code: str) -> None:
    """Removes site from list based on unique shortcode"""
    conn = get_db_connection()
    try:
        conn.execute('''
            DELETE from sites 
            where code=?''', (code,))
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

    return None

def add_initials(initials: str) -> None:
    """Adds participants initials to roster"""

    conn = get_db_connection()
    try:
        conn.execute("""
            INSERT into initials (name)
            values (?)
            """, (initials,))
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

    return None

def remove_initials(initials: str) -> None:
    """Removes participants initials from roster. Used only for leavers."""
    conn = get_db_connection()
    try:
        conn.execute('''
            DELETE from initials 
            where name=?''', (initials,))
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

    return None

def add_to_sked(site: str, day: str, initials: str) -> None:
    """Adds existing student to worksite schedule"""
    conn = get_db_connection()
    print(f"foreign keys state: {conn.execute("""PRAGMA foreign_keys;""").fetchall()}")

    insert_statement = """
    INSERT INTO schedule(workday, site_id, initials_id)
    VALUES (
        ?,
        (SELECT id FROM sites WHERE code=?),
        (SELECT id FROM initials WHERE name=?)
    );
    """
    try:
        conn.execute(insert_statement, (day, site, initials))
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

    return None

def remove_from_sked(site: str, day: str, initials: str) -> None:
    """removes existing student from worksite schedule"""
    conn = get_db_connection()
    print(f"foreign keys state: {conn.execute("""PRAGMA foreign_keys;""").fetchall()}")

    delete_statement = """
    DELETE from schedule
    WHERE workday=?
    AND site_id = (SELECT id FROM sites WHERE code=?)
    AND initials_id = (SELECT id FROM initials WHERE name=?);
    """
    try:
        conn.execute(delete_statement, (day, site, initials))
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

    return None