class MetadataReader:

    def __init__(self, connection):
        self.connection = connection

    def get_tables(self):

        sql = """
            SELECT
                TABLE_NAME,
                TABLE_TYPE,
                ENGINE,
                TABLE_ROWS,
                CREATE_TIME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            ORDER BY TABLE_NAME
        """

        with self.connection.cursor() as cursor:

            cursor.execute(sql)

            rows = cursor.fetchall()

        tables = []

        for row in rows:

            tables.append({
                "table_name": row[0],
                "table_type": row[1],
                "engine": row[2],
                "rows": row[3],
                "created": row[4]
            })

        return tables

    def get_columns(self, table_name):

        query = """
        SELECT
            COLUMN_NAME,
            COLUMN_TYPE,
            IS_NULLABLE,
            COLUMN_DEFAULT,
            COLUMN_KEY,
            EXTRA,
            COLUMN_COMMENT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query, (table_name,))
            rows = cursor.fetchall()
        columns = []

        for row in rows:
            columns.append({
                "column_name": row[0],
                "column_type": row[1],
                "nullable": row[2],
                "default": row[3],
                "key": row[4],
                "extra": row[5],
                "comment": row[6]
            })
        return columns


    def get_primary_keys(self, table_name):
        sql = """
        SELECT
            COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE
            TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = %s
            AND CONSTRAINT_NAME='PRIMARY'
        ORDER BY ORDINAL_POSITION
        """

        with self.connection.cursor() as cursor:
            cursor.execute(sql, (table_name,))
            rows = cursor.fetchall()

        primary_keys = []
        for row in rows:
            primary_keys.append({
                "column_name": row[0]
            })
        return primary_keys

    def get_foreign_keys(self, table_name):
        sql = """
        SELECT
            COLUMN_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE
            TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = %s
            AND REFERENCED_TABLE_NAME IS NOT NULL
        ORDER BY COLUMN_NAME
        """

        with self.connection.cursor() as cursor:

            cursor.execute(sql, (table_name,))
            rows = cursor.fetchall()

        foreign_keys = []
        for row in rows:
            foreign_keys.append({
                "column_name": row[0],
                "referenced_table": row[1],
                "referenced_column": row[2]
            })
        return foreign_keys

    def get_indexes(self, table_name):
        sql = """
        SELECT
            INDEX_NAME,
            COLUMN_NAME,
            NON_UNIQUE
        FROM information_schema.STATISTICS
        WHERE
            TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = %s
        ORDER BY INDEX_NAME, SEQ_IN_INDEX
        """

        with self.connection.cursor() as cursor:

            cursor.execute(sql, (table_name,))
            rows = cursor.fetchall()
        indexes = []
        for row in rows:
            indexes.append({
                "index_name": row[0],
                "column_name": row[1],
                "non_unique": row[2]
            })
        return indexes