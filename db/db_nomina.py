import logging
from typing import Dict, List

from utils.jsons_utils import save_json_file
from utils.serializations import serialize_value  # importa tu helper


# Funcion para obtener los datos de SCPTrabajadores segun el query necesario
# para el JSON
def get_trabajadores(db) -> List[Dict]:
    doctype_name = "Employee"
    sqlserver_name = "SCPTRABAJADORES"
    module_name = "Setup"

    # Definimos un mapeo explícito de campos
    field_mapping = [
        # Campos del doctype principal (trabajador)
        # (alias, (sql_field, doctype_field_type))
        ("identity_number", ("T.CPTrabConsecutivoID", 'string')),
        ("first_name", ("T.CPTrabNombre", 'string')),
        ("last_name", ("T.CPTrabPriApellido", 'string')),
        ("second_surname", ("T.CPTrabSegApellido", 'string')),
        ("gender", ("T.TrabSexo", 'string')),
        ("occupational_category", ("C.CategODescripcion", 'string')),
        ("designation", ("CAR.CargDescripcion", 'string')),
        ("employment_type", ("TT.TipTrabDescripcion", 'string')),
        ("date_of_joining", ("T.TrabFechaAlta", 'string')),
        ("contract_end_date", ("T.TrabFechaBaja", 'string')),
        ("salary_mode", ("T.TrabFormaCobro", 'numeric')),  # es un
        # campo select por lo que le pongo true para que aparezca el numero
        # sin comillas
        ("banc_ac_no", ("T.TrabTmagnMN", 'string')),
        ("company_email", ("T.TrabCorreo", 'string')),
        ("accumulate_vacations", ("T.TrabCPVacaciones", 'string')),
        ("current_address", ("PD.SRHPersDireccionDir", 'string')),
        ("permanent_address", ("PD.SRHPersDireccionOficial", 'string')),
        ("state_province", ("R.ProvCod", 'string')),
        ("city_town", ("R.MunicCod", 'string')),
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
    SELECT
        {', '.join(select_clauses)}
    FROM SCPTrabajadores AS T
    LEFT JOIN SNOCARGOS AS CAR ON T.CargId = CAR.CargId
    LEFT JOIN SNOCATEGOCUP AS C ON T.CategId = C.CategId
    LEFT JOIN SNOTIPOTRABAJADOR AS TT ON T.TipTrabId = TT.TipTrabId
    LEFT JOIN SRHPersonas AS P ON T.CPTrabConsecutivoID = P.SRHPersonasId
    LEFT JOIN SRHPersonasDireccion AS PD ON P.SRHPersonasId = PD.SRHPersonasId
    LEFT JOIN TEREPARTOS AS R ON PD.TRepartosCodigo = R.TRepartosCodigo
    WHERE (T.TrabDesactivado = '' OR T.TrabDesactivado IS NULL)
    """

    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            # Creamos un diccionario de tipos por campo
            field_types = {alias: field_type for alias, (_, field_type) in
                           field_mapping}
            result = []
            for row in rows:
                employee_data = {}
                for col, val in zip(columns, row):
                    field_type = field_types.get(col, 'auto')
                    employee_data[col] = serialize_value(val, field_type)

                result.append(employee_data)
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(
                f"{doctype_name}.json guardado correctamente en {output_path}")

            return result

    except Exception as e:
        logging.error(f"Error al obtener SCPTrabajadores: {e}")
        raise Exception(f"Error al obtener datos de SCPTrabajadores: {str(e)}")


# Prepara la relacion entre las tablas con SCPTrabajadores y las muestra en
# el frontend
def get_relaciones_trabajadores(db) -> List[Dict]:
    query = """
    SELECT
        fk.table_name AS source_table,
        fk.column_name AS source_column,
        pk.table_name AS target_table,
        pk.column_name AS target_column
    FROM
        information_schema.referential_constraints rc
    JOIN
        information_schema.key_column_usage fk ON rc.constraint_name = 
        fk.constraint_name
    JOIN
        information_schema.key_column_usage pk ON rc.unique_constraint_name = 
        pk.constraint_name
    WHERE
        fk.table_name IN ('SCPTrabajadores', 'SNOCARGOS', 
        'SNOTIPOTRABAJADOR', 'SRHPersonas', 'SRHPersonasDireccion', 
        'TEREPARTOS')
        OR pk.table_name IN ('SCPTrabajadores', 'SNOCARGOS', 
        'SNOTIPOTRABAJADOR', 'SRHPersonas', 'SRHPersonasDireccion', 
        'TEREPARTOS')
    """

    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            return [
                {
                    "source_table": row[0],
                    "source_column": row[1],
                    "target_table": row[2],
                    "target_column": row[3],
                }
                for row in rows
            ]
    except Exception as e:
        logging.error(f"Error al obtener relaciones entre tablas: {e}")
        raise


def construir_tree_trabajadores(relaciones):
    tree = {}
    counter = 1  # para generar IDs únicos

    for rel in relaciones:
        src = rel["source_table"]
        tgt = rel["target_table"]
        src_col = rel["source_column"]
        tgt_col = rel["target_column"]

        if src not in tree:
            tree[src] = {
                "id": src,
                "description": f"Relaciones desde {src}",
                "children": {},
            }

        if tgt not in tree[src]["children"]:
            tree[src]["children"][tgt] = {
                "id": f"{src}_{tgt}",
                "description": f"Relaciones hacia {tgt}",
                "children": [],
            }

        tree[src]["children"][tgt]["children"].append(
            {"id": f"rel_{counter}",
             "description": f"{src_col} → {tgt}.{tgt_col}"}
        )

        counter += 1

    # convertir a lista y formatear recursivamente
    return [
        {
            "id": src_node["id"],
            "description": src_node["description"],
            "children": list(tgt_dict.values()),
        }
        for src_node in tree.values()
        for tgt_dict in [src_node["children"]]
    ]


# Para obtener las categorias ocupacionales y poniendo alias con el nombre
# del campo en el doctype
def get_categorias_ocupacionales(db):
    doctype_name = "Occupational Category"
    sqlserver_name = "SNOCATEGOCUP"
    module_name = "Cuba"

    query = """
        SELECT CategODescripcion as category_name
        FROM SNOCATEGOCUP
        WHERE CategDesactivado = ' ' OR CategDesactivado IS NULL
    """

    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]

            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(
                f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(
            f"Error al obtener datos de las categorias ocupacionales: {e}")
        raise


# Para obtener los cargos de los trabajadores
# No le pongo field_mapping por ser un solo campo tipo texto
def get_cargos_trabajadores(db):
    doctype_name = "Designation"
    sqlserver_name = "SNOCARGOS"
    module_name = "Setup"
    query = """
        SELECT CargDescripcion as designation_name
        FROM SNOCARGOS
        WHERE CargDesactivado  = '' OR CargDesactivado IS NULL
    """
    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            # serializando los campos para que no de error los decimales
            result = [
                {key: serialize_value(value) for key, value in
                 zip(columns, row)}
                for row in rows
            ]
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(
                f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(
            f"Error al obtener datos de los cargos de los trabajadores: {e}")
        raise


# Para obtener los tipos de trabajadores
# No field_mapping por ser solo campo tipo texto
def get_tipos_trabajadores(db):
    doctype_name = "Employment Type"
    sqlserver_name = "SNOCTIPOTRABAJADOR"
    module_name = "HR"
    query = """
        SELECT TipTrabDescripcion as employee_type_name
        FROM SNOTIPOTRABAJADOR s
        WHERE TipTrabDesactivado  = '' OR TipTrabDesactivado IS NULL
    """
    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            # serializando los campos para que no de error los decimales
            result = [
                {key: serialize_value(value) for key, value in
                 zip(columns, row)}
                for row in rows
            ]
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(
                f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(
            f"Error al obtener datos de los tipos de trabajadores: {e}")
        raise


# Para obtener los tipos de  retenciones
def get_tipos_retenciones(db):
    doctype_name = "Withholding Type"
    sqlserver_name = "SCPCONRETPAGAR"
    module_name = "Cuba"

    # Mapeo de campos con información adicional sobre su tipo
    field_mapping = [
        # (alias, (sql_field, doctype_field_type))
        ("withholding_type_name", ("CPCRetDescripcion", 'string')),
        ("debt_to", ("CRetDeudaCon", 'integer')),
        ("account", ("c.ClcuDescripcion", 'string')),
        ("priority", ("CRetPPrioridad", 'integer')),
        ("child_support", ("CRetPPenAlimenticia", 'boolean')),
        ("by_installments", ("CRetPConPlazos", 'integer'))
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]
    query = f"""
        SELECT 
            {', '.join(select_clauses)}
        FROM SCPCONRETPAGAR s LEFT JOIN SCGCLASIFICADORDECUENTAS c ON 
        s.ClcuIDCuenta = c.ClcuIDCuenta
        WHERE CRetPDesactivado  = '' OR CRetPDesactivado IS NULL
    """
    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            # serializando los campos
            # result = [
            #     {key: serialize_value(value) for key, value in
            #      zip(columns, row)}
            #     for row in rows
            # ]

            field_type_map = {alias: field_type for alias, (_, field_type) in
                              field_mapping}
            result = [
                {
                    key: serialize_value(value, field_type_map[key])
                    for key, value in zip(columns, row)
                }
                for row in rows
            ]

            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(
                f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(
            f"Error al obtener datos de los tipos de retenciones: {e}")
        raise


# Para obtener maestro de  retenciones
def get_maestro_retenciones(db):
    doctype_name = "XXXXXX"
    sqlserver_name = "SCPMAESTRORETENCION"
    module_name = "XXXXXX"

    # Mapeo de campos con información adicional sobre su tipo
    field_mapping = [
        # (alias, (sql_field, doctype_field_type))
        ("employee_name",
         ("s2.CPTrabNombre + ' ' + s2.CPTrabPriApellido + ' ' + "
          "s2.CPTrabSegApellido",
          'string')),
        ("withholding_type", ("s.CPCRetPCodigo", 'string')),
        # ("banking_record", ("", '')),
        ("debt", ("s.RetDeuda", 'decimal')),
        ("term_amount", ("s.RetPlazo", 'decimal')),
        ("payroll_frecuency", ("s.PeriCodigo", 'integer')),
        ("fortnight", ("s.CorteCodigo", 'integer')),
        ("from_date", ("s.RetFechaAlta", 'date')),
        ("salary_component", ("", '')),
        ("customer", ("", '')),
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
        SELECT
            {', '.join(select_clauses)}
        from
            SCPMAESTRORETENCION s
        left join SCPTRABAJADORES s2 on s.CPTrabConsecutivoID = 
        s2.CPTrabConsecutivoID
        where
             (s2.TrabDesactivado = '' or s2.TrabDesactivado IS NULL) AND 
             s.RetCantPlazo <= 6 
    """
    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            # serializando los campos para que no de error los decimales
            result = [
                {key: serialize_value(value) for key, value in
                 zip(columns, row)}
                for row in rows
            ]
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(
                f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(
            f"Error al obtener datos del maestro de retenciones: {e}")
        raise


# Para obtener loa pensionados
def get_pensionados(db):
    doctype_name = "Customer"
    sqlserver_name = "SNOMANTPENS"
    module_name = "Selling"

    field_mapping = [
        # (alias, (sql_field, doctype_field_type))
        ("customer_name", ("MantPensNombre + ' ' + MantPensPriApe + ' ' + "
                           "MantPensSegApe", 'string')),
        ("customer_primary_address", ("MantPensDir", 'string')),
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
        SELECT 
        {', '.join(select_clauses)}
        FROM SNOMANTPENS
        WHERE MantPensDesactivada  = '' OR MantPensDesactivada IS NULL
    """
    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            # serializando los campos para que no de error los decimales
            result = [
                {key: serialize_value(value) for key, value in
                 zip(columns, row)}
                for row in rows
            ]
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(
                f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de los pensionados: {e}")
        raise


# Para obtener tasas de destajo
def get_tasas_destajos(db):
    doctype_name = "Item Price"
    sqlserver_name = "SNONOMENCLADORTASASDESTAJO"
    module_name = "Stock"
    field_mapping = [
        # (alias, (sql_field, doctype_field_type))
        ("item_name", ("TasaDDescripcion", 'string')),
        ("price_list_rate", ("TasaDTasa", 'currency')),
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
        SELECT 
            {', '.join(select_clauses)}
        FROM SNONOMENCLADORTASASDESTAJO
        WHERE TasaDesactivado  != '' OR TasaDesactivado IS NULL
    """
    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            # serializando los campos para que no de error los decimales
            result = [
                {key: serialize_value(value) for key, value in
                 zip(columns, row)}
                for row in rows
            ]
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(
                f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de las tasas de destajos: {e}")
        raise


# Para obtener colectivos
def get_colectivos(db):
    doctype_name = "Employee Group"
    sqlserver_name = "SNONOMENCLADORCOLECTIVOS"
    module_name = "Setup"

    field_mapping = [
        # (alias, (sql_field, doctype_field_type))
        ("employee_group_name", ("ColecDescripcion", 'string')),
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
        SELECT 
            {', '.join(select_clauses)}
        FROM SNONOMENCLADORCOLECTIVOS
        WHERE ColecDesactivado  != '' OR ColecDesactivado IS NOT NULL
    """
    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            # serializando los campos para que no de error los decimales
            result = [
                {key: serialize_value(value) for key, value in
                 zip(columns, row)}
                for row in rows
            ]
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(
                f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de los colectivos: {e}")
        raise


# Para obtener colectivos
def get_departamentos(db):
    doctype_name = "Department"
    sqlserver_name = "SMGAREASUBAREA"
    module_name = "Setup"

    field_mapping = [
        # (alias, (sql_field, doctype_field_type))
        ("parent_department",
         ("CASE WHEN s1.sareaDescrip IS NULL THEN NULL ELSE s.AreaDescrip END",
          'string')),
        ("department_name",
         ("CASE WHEN s1.sareaDescrip IS NULL THEN s.AreaDescrip ELSE "
          "s1.sareaDescrip END",
          'string')),
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
        SELECT
            {', '.join(select_clauses)}
        FROM
            S5Principal.dbo.SMGAREASUBAREA s
        LEFT JOIN
            S5Principal.dbo.SMGAREASUBAREA1 s1 ON s.AreaCodigo = s1.AreaCodigo;
        """
    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            # serializando los campos para que no de error los decimales
            result = [
                {key: serialize_value(value) for key, value in
                 zip(columns, row)}
                for row in rows
            ]
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(
                f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de los departamentos: {e}")
        raise
