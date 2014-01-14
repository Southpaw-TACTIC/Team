

import tacticenv

from pyasm.security import Batch
Batch()
from pyasm.search import DbContainer, Search


def fix_work_hour_id():

    db = DbContainer.get("sthpw")

    sql = '''
BEGIN TRANSACTION;

CREATE TABLE t_backup (
    id integer PRIMARY KEY AUTOINCREMENT,
    code character varying(256),
    project_code character varying(256),
    description text,
    category character varying(256),
    process character varying(256),
    "login" character varying(256),
    "day" timestamp without time zone,
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    straight_time double precision,
    over_time double precision,
    search_type character varying(256),
    search_id integer,
    status character varying(256),
    task_code character varying(256),
    CONSTRAINT "work_hour_code_idx" UNIQUE (code)
);
INSERT INTO t_backup SELECT id, code, project_code, description, category, process, "login", "day", start_time, end_time, straight_time, over_time, search_type, search_id, status, task_code FROM %(table)s;


DROP TABLE %(table)s;
ALTER TABLE t_backup RENAME TO %(table)s;
COMMIT;

    ''' % {"table": "work_hour"}

    conn = db.conn
    conn.executescript(sql)


def fix_notification_log_id():

    db = DbContainer.get("sthpw")

    sql = '''
BEGIN TRANSACTION;

CREATE TABLE t_backup (
    id integer PRIMARY KEY AUTOINCREMENT,
    project_code character varying(256),
    "login" character varying(256),
    command_cls character varying(256),
    subject text,
    message text,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO t_backup SELECT id, project_code, "login", command_cls, subject, message, "timestamp" FROM %(table)s;

DROP TABLE %(table)s;
ALTER TABLE t_backup RENAME TO %(table)s;
COMMIT;

    ''' % {"table": "notification_log"}

    conn = db.conn
    conn.executescript(sql)



def fix_notification_login_id():

    db = DbContainer.get("sthpw")

    sql = '''
BEGIN TRANSACTION;

CREATE TABLE t_backup (
    id integer PRIMARY KEY AUTOINCREMENT,
    notification_log_id integer,
    "login" character varying(256),
    "type" character varying(256),
    project_code character varying(256),
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO t_backup SELECT id, notification_log_id, "login", "type", project_code, "timestamp" FROM %(table)s;

DROP TABLE %(table)s;
ALTER TABLE t_backup RENAME TO %(table)s;
COMMIT;

    ''' % {"table": "notification_login"}

    conn = db.conn
    conn.executescript(sql)

   

def fix_debug_log_id():

    db = DbContainer.get("sthpw")

    sql = '''
BEGIN TRANSACTION;

CREATE TABLE t_backup (
    id integer PRIMARY KEY AUTOINCREMENT,
    "category" character varying(256),
    "level" character varying(256),
    "message" text,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "login" character varying(256),
    "s_status" character varying(30)
);

INSERT INTO t_backup SELECT "id", "category", "level", "message", "timestamp", "login", "s_status" FROM %(table)s;

DROP TABLE %(table)s;
ALTER TABLE t_backup RENAME TO %(table)s;
COMMIT;

    ''' % {"table": "debug_log"}

    conn = db.conn
    conn.executescript(sql)

   


if __name__ == '__main__':
    fix_work_hour_id()
    fix_notification_log_id()
    fix_notification_login_id()
    fix_debug_log_id()


