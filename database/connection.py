import pymysql
from sshtunnel import SSHTunnelForwarder


class DatabaseConnection:

    def __init__(self):
        self.connection = None
        self.tunnel = None

    def connect_direct(
        self,
        host,
        port,
        database,
        username,
        password
    ):

        self.connection = pymysql.connect(
            host=host,
            port=int(port),
            user=username,
            password=password,
            database=database
        )

        return self.connection

    def connect_ssh(
        self,
        ssh_host,
        ssh_port,
        ssh_user,
        pem_file,
        db_host,
        db_port,
        db_name,
        db_user,
        db_password
    ):

        self.tunnel = SSHTunnelForwarder(
            (ssh_host, int(ssh_port)),
            ssh_username=ssh_user,
            ssh_pkey=pem_file,
            remote_bind_address=(
                db_host,
                int(db_port)
            )
        )

        self.tunnel.start()

        self.connection = pymysql.connect(
            host='127.0.0.1',
            port=self.tunnel.local_bind_port,
            user=db_user,
            password=db_password,
            database=db_name
        )

        return self.connection

    def close(self):

        if self.connection:
            self.connection.close()

        if self.tunnel:
            self.tunnel.stop()