class SchemaReader:

    def __init__(self, connection):
        self.connection = connection

    def get_tables(self):

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT
                TABLE_NAME,
                TABLE_TYPE
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            ORDER BY TABLE_NAME
        """)

        rows = cursor.fetchall()

        tables = []

        for row in rows:

            tables.append({
                "table_name": row[0],
                "table_type": row[1]
            })

        return tables

    def get_columns(self, table_name):

        cursor = self.connection.cursor()

        cursor.execute(f"""
            SHOW COLUMNS
            FROM {table_name}
        """)

        rows = cursor.fetchall()

        columns = []

        for row in rows:

            columns.append({
                "name": row[0],
                "type": row[1]
            })

        return columns