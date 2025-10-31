import reflex as rx
import os
import psycopg2
from typing import TypedDict, Any
import logging
import base64
import json
from .credentials_state import CredentialsState
from sshtunnel import SSHTunnelForwarder
import io
import paramiko


class ColumnInfo(TypedDict):
    name: str
    type: str


class TableInfo(TypedDict):
    name: str
    columns: list[ColumnInfo]


class DatabaseState(rx.State):
    tables: list[TableInfo] = []
    is_connected: bool = False
    connection_error: str = ""

    @rx.var
    def table_names(self) -> list[str]:
        """Return a list of table names."""
        return [table["name"] for table in self.tables]

    async def _get_db_conn(self):
        creds_state = await self.get_state(CredentialsState)
        if not creds_state or not creds_state.active_environment:
            self.connection_error = "No active database environment selected."
            self.is_connected = False
            return None
        env = creds_state.get_active_env
        if not env:
            self.connection_error = "Active environment not found."
            self.is_connected = False
            return None
        if env.ssh_host and env.ssh_user and env.ssh_key:
            try:
                pkey = self._parse_ssh_key(env.ssh_key)
                if not pkey:
                    raise paramiko.SSHException(
                        "Unsupported or invalid SSH private key format"
                    )
                tunnel = SSHTunnelForwarder(
                    (env.ssh_host, env.ssh_port),
                    ssh_username=env.ssh_user,
                    ssh_pkey=pkey,
                    remote_bind_address=(env.host, env.port),
                )
                tunnel.start()
                self.set_vars(tunnel=tunnel)
                db_host = tunnel.local_bind_host
                db_port = tunnel.local_bind_port
            except Exception as e:
                logging.exception(f"SSH tunnel failed: {e}")
                self.connection_error = f"SSH tunnel failed: {e}"
                self.is_connected = False
                return None
        else:
            db_host = env.host
            db_port = env.port
        db_url = f"postgresql://{env.username}:{env.password}@{db_host}:{db_port}/{env.database}"
        try:
            conn = psycopg2.connect(dsn=db_url, connect_timeout=3)
            return conn
        except Exception as e:
            logging.exception(f"Error connecting to database: {e}")
            error_message = str(e).split("""
""")[0]
            self.connection_error = f"Failed to connect: {error_message}"
            self.is_connected = False
            return None

    @rx.event
    async def fetch_schema(self):
        """Connect to the database and fetch the schema."""
        conn = await self._get_db_conn()
        if not conn:
            return
        self.is_connected = True
        self.connection_error = ""
        self.tables = []
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
                """)
                tables = [row[0] for row in cur.fetchall()]
                table_info_list = []
                for table_name in tables:
                    cur.execute(
                        """
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = %s;
                    """,
                        (table_name,),
                    )
                    columns = cur.fetchall()
                    column_info: list[ColumnInfo] = [
                        {"name": col[0], "type": col[1]} for col in columns
                    ]
                    table_info_list.append({"name": table_name, "columns": column_info})
                self.tables = table_info_list
        except Exception as e:
            logging.exception(f"Error fetching schema: {e}")
            self.connection_error = f"An error occurred while fetching the schema: {e}"
        finally:
            if conn:
                conn.close()
            if hasattr(self, "tunnel") and self.tunnel:
                self.tunnel.stop()
                self.set_vars(tunnel=None)

    def _parse_ssh_key(self, key_string: str):
        """Parse SSH private key from string, trying multiple key types."""
        key_types = [paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey]
        for key_class in key_types:
            try:
                key_file = io.StringIO(key_string)
                return key_class.from_private_key(key_file)
            except paramiko.SSHException as e:
                logging.exception(
                    f"Failed to parse SSH key with {key_class.__name__}: {e}"
                )
                continue
        return None