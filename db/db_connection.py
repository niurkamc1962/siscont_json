# db/db_connection.py
# conexion a la base de datos sqlserver

import json
from contextlib import contextmanager
from os import makedirs, path
from typing import Any, Dict, List

import pyodbc

from config import get_settings
from db.db_manager import ConexionParams
from utils.serializations import is_serializable, serialize_value

settings = get_settings()


class DatabaseManager:
    def __init__(self, host: str, password: str, database: str, port: str, user: str):
        self.connection_params = {
            "host": host,
            "password": password,
            "database": database,
            "port": port,
            "user": user,
        }
        self._conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        if self._conn is None:
            print(f"Conectando con parámetros: {self.connection_params}")
            self._conn = self._create_connection()
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def _create_connection(self):
        url = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.connection_params['host']};"
            f"PORT={self.connection_params['port']};"
            f"DATABASE={self.connection_params['database']};"
            f"UID={self.connection_params['user']};"
            f"PWD={self.connection_params['password']};"
            f"Timeout=0"
        )
        try:
            return pyodbc.connect(url)
        except pyodbc.Error as ex:
            print(f"Error al conectar: {ex}")
            raise

    @contextmanager
    def cursor(self):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    def get_all_tables(self) -> Dict[str, Any]:
        with self.cursor() as cursor:
            cursor.execute(
                "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
            )
            tables = [row.TABLE_NAME for row in cursor.fetchall()]
            return {"tables": tables, "total_tables": len(tables)}

    def get_table_structure(self, table_name: str) -> List[Dict]:
        with self.cursor() as cursor:
            cursor.execute(
                """
                SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = ?
                """,
                table_name,
            )
            return [
                {
                    "column_name": column.COLUMN_NAME,
                    "data_type": column.DATA_TYPE,
                    "max_length": column.CHARACTER_MAXIMUM_LENGTH,
                    "is_nullable": column.IS_NULLABLE,
                }
                for column in cursor.fetchall()
            ]

    def get_table_relations(self, table_name: str) -> List[Dict[str, Any]]:
        try:
            with self.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        OBJECT_NAME(f.parent_object_id) AS tabla_padre,
                        COL_NAME(fc.parent_object_id, fc.parent_column_id) AS columna_padre,
                        OBJECT_NAME(f.referenced_object_id) AS tabla_hija,
                        COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS columna_hija
                    FROM
                        sys.foreign_keys f
                    INNER JOIN
                        sys.foreign_key_columns fc ON f.object_id = fc.constraint_object_id
                    WHERE
                        OBJECT_NAME(f.parent_object_id) = '{table_name}'
                    OR
                        OBJECT_NAME(f.referenced_object_id) = '{table_name}'
                """
                )
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error al obtener relaciones de {table_name}: {e}")
            raise

    def get_all_relations(self) -> List[Dict]:
        try:
            with self.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        OBJECT_NAME(f.parent_object_id) AS tabla_padre,
                        COL_NAME(fc.parent_object_id, fc.parent_column_id) AS columna_padre,
                        OBJECT_NAME(f.referenced_object_id) AS tabla_hija,
                        COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS columna_hija
                    FROM
                        sys.foreign_keys f
                    INNER JOIN
                        sys.foreign_key_columns fc ON f.object_id = fc.constraint_object_id
                """
                )
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error al obtener relaciones: {e}")
            raise

    def export_table_to_json(
        self, table_name: str, fields: List[str], output_folder: str = "formatos_json"
    ) -> Dict[str, Any]:
        if not path.exists(output_folder):
            makedirs(output_folder)

        with self.cursor() as cursor:
            query = f"SELECT {', '.join(fields)} FROM {table_name}"
            cursor.execute(query)

            columns = [column[0] for column in cursor.description]
            table_data = []

            for row in cursor.fetchall():
                row_data = {
                    columns[i]: (
                        serialize_value(row[i])
                        if not is_serializable(row[i])
                        else row[i]
                    )
                    for i in range(len(columns))
                }
                table_data.append(row_data)

        file_path = path.join(output_folder, f"{table_name}.json")
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(
                {"table_name": table_name, "data": table_data},
                json_file,
                indent=4,
                ensure_ascii=False,
            )

        return {"table_name": table_name, "data": table_data}


def create_db_manager(params: ConexionParams) -> DatabaseManager:
    return DatabaseManager(
        host=params.host,
        password=params.password,
        database=params.database,
        port=str(settings.SQL_PORT),
        user=settings.SQL_USER,
    )
