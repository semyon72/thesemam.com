# Project: blog_7myon_com
# Package: 
# Filename: db_patches.py
# Generated: 2021 May 19 at 21:41 
# Description of <db_patches>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
import functools

from django.db import DEFAULT_DB_ALIAS, connections
from django.db.backends.signals import connection_created
from django.db.backends.sqlite3.base import none_guard

from django.utils.version import PY38

from blog.text_tools import strip_tags


STRIP_TAGS_FUNCTION_NAME='strip_tags'

class PatchBase:
    name = ''

    def patch(self):
        pass


class SQLitePatch(PatchBase):
    name = 'sqlite'

    @staticmethod
    def strip_tag(t):
        return strip_tags(t)

    def patch(self):
        def on_connection_created(sender, **kwargs):
            conn = kwargs['connection'].connection
            # it partially have gotten from sqlite3.base.DatabaseWrapper.get_new_connection(...)
            if PY38:
                create_deterministic_function = functools.partial(
                    conn.create_function,
                    deterministic=True,
                )
            else:
                create_deterministic_function = conn.create_function
            create_deterministic_function(STRIP_TAGS_FUNCTION_NAME, 1, self.strip_tag)

        connection_created.connect(receiver=on_connection_created, weak=False, dispatch_uid=hash(self))


class MySQLPatch(PatchBase):
    """
        Implementation stored function 'strip_tags' for MySQL

        /* https://stackoverflow.com/a/13346684 */
        DROP FUNCTION IF EXISTS strip_tags;
        DELIMITER |
        CREATE FUNCTION strip_tags($str text) RETURNS text
        BEGIN
            DECLARE $start, $end INT DEFAULT 1;
            LOOP
                SET $start = LOCATE("<", $str, $start);
                IF (!$start) THEN RETURN $str; END IF;
                SET $end = LOCATE(">", $str, $start);
                IF (!$end) THEN SET $end = $start; END IF;
                SET $str = INSERT($str, $start, $end - $start + 1, "");
            END LOOP;
        END; |
        DELIMITER ;

        Test
        SELECT STRIP_TAGS('<span>hel<b>lo <a href="world">wo<>rld</a> <<x>again<.') REGEXP '.*Hello.+wo.+ag.*' as `clean_text`;
    """

    name = 'mysql'

    def _test_strip_tags(self, cursor):
        test_str = '<span>hel<b>lo <a href="world">wo<>rld</a> <<x>again<.'
        rstr = 'hello world again.'
        cursor.execute('SELECT %s(%%s)' % (STRIP_TAGS_FUNCTION_NAME, ), (test_str, ))
        row = cursor.fetchone()
        return row[0] == rstr

    def _is_strip_tags_exists(self, cursor):
        sql = 'SHOW FUNCTION STATUS WHERE name = %s'
        cursor.execute(sql, (STRIP_TAGS_FUNCTION_NAME,))
        rows = cursor.fetchall()
        return len(rows) == 1

    def _create_strip_tags_stored_function(self, cursor):
        sql = """
        CREATE FUNCTION %s($str text) RETURNS text
        BEGIN
            DECLARE $start, $end INT DEFAULT 1;
            LOOP
                SET $start = LOCATE("<", $str, $start);
                IF (!$start) THEN RETURN $str; END IF;
                SET $end = LOCATE(">", $str, $start);
                IF (!$end) THEN SET $end = $start; END IF;
                SET $str = INSERT($str, $start, $end - $start + 1, "");
            END LOOP;
        END;
        """
        cursor.execute(sql % (STRIP_TAGS_FUNCTION_NAME, ))

    def patch(self):
        with connections[DEFAULT_DB_ALIAS].cursor() as cursor:
            if not self._is_strip_tags_exists(cursor):
                self._create_strip_tags_stored_function(cursor)
            if not self._test_strip_tags(cursor):
                raise AssertionError('Probably \'%s\' function works improperly.' % STRIP_TAGS_FUNCTION_NAME)


defined_patch_list = (SQLitePatch, MySQLPatch)
"""
    It could be initialized automatically
"""


def get_patch():
    connection = connections[DEFAULT_DB_ALIAS]
    patches = tuple(patch for patch in defined_patch_list if connection.vendor == patch.name)
    if len(patches) > 0:
        return patches[0]()

    return PatchBase()
