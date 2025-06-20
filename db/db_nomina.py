import datetime
import logging
from typing import Dict, List

from utils.jsons_utils import export_table_to_json, \
    export_table_to_json_paginated


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
        ("department", ("T.AreaCodigo", 'integer'))
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
    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query
    )


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

    field_mapping = [
        # Campos del doctype principal (trabajador)
        # (alias, (sql_field, doctype_field_type))
        ("category_name", ("CategODescripcion", 'string'))
    ]
    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
       SELECT
           {', '.join(select_clauses)}
        FROM SNOCATEGOCUP
        WHERE CategDesactivado = ' ' OR CategDesactivado IS NULL
    """

    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query
    )


# Para obtener los cargos de los trabajadores
# No le pongo field_mapping por ser un solo campo tipo texto
def get_cargos_trabajadores(db):
    doctype_name = "Designation"
    sqlserver_name = "SNOCARGOS"
    module_name = "Setup"

    field_mapping = [
        # Campos del doctype principal (trabajador)
        # (alias, (sql_field, doctype_field_type))
        ("designation_name", ("CargDescripcion", 'string'))
    ]
    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
           SELECT
               {', '.join(select_clauses)}
            FROM SNOCARGOS
            WHERE CargDesactivado  = '' OR CargDesactivado IS NULL
        """
    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query
    )


# Para obtener los tipos de trabajadores
# No field_mapping por ser solo campo tipo texto
def get_tipos_trabajadores(db):
    doctype_name = "Employment Type"
    sqlserver_name = "SNOCTIPOTRABAJADOR"
    module_name = "HR"

    field_mapping = [
        # Campos del doctype principal (trabajador)
        # (alias, (sql_field, doctype_field_type))
        ("employee_type_name", ("TipTrabDescripcion", 'string'))
    ]
    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
          SELECT
                  {', '.join(select_clauses)}
            FROM SNOTIPOTRABAJADOR s
            WHERE TipTrabDesactivado  = '' OR TipTrabDesactivado IS NULL
        """
    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query
    )


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
    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query
    )


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
    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query
    )


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
    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query
    )


# Para obtener tasas de destajo
def get_tasas_destajos(db):
    doctype_name = "Item Price"
    sqlserver_name = "SNONOMENCLADORTASASDESTAJO"
    module_name = "Stock"
    field_mapping = [
        # (alias, (sql_field, doctype_field_type))
        ("item_name", ("TasaDDescripcion", 'string')),
        ("price_list_rate", ("TasaDTasa", 'float'))
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
    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query
    )


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
    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query
    )


# Para obtener departamentos
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
    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query
    )


# Para submayor de vacaciones
def get_submayor_vacaciones(db):
    doctype_name = "Employee Opening Vacation Subledger"
    sqlserver_name = "SNOSMVACACIONES"
    module_name = "Cuba"

    field_mapping = [
        ("initial_balance_in_amount", ("MAX(s.SMVacSaldoInicialI)", "float")),
        ("initial_balance_in_days", ("MAX(s.SMVacSaldoInicialD)", "float")),
        ("employee",
         ("MAX(s2.CPTrabNombre + ' ' + s2.CPTrabPriApellido + ' ' +  "
          "s2.CPTrabSegApellido)",
          "string")),
        ("expediente_laboral", ("MAX(s2.CPTrabExp)", "string")),
        ("SMVacId", ("MAX(s.SMVacId)", "integer")),
    ]

    base_query_from = """
        FROM S5Principal.dbo.SNOSMVACACIONES s
        JOIN S5Principal.dbo.SCPTRABAJADORES s2
            ON s.CPTrabConsecutivoID = s2.CPTrabConsecutivoID
        WHERE (s.SMVacDesactivado = '' AND s2.TrabDesactivado = '')
            AND s.SMVacSaldoInicialD > 0
        GROUP BY s.CPTrabConsecutivoID
    """

    order_clause = "ORDER BY MAX(s.SMVacId) DESC"

    return export_table_to_json_paginated(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        base_query_from=base_query_from,
        order_clause=order_clause
    )


# Para submayor de salarios no reclamados
def get_submayor_salarios_no_reclamados(db):
    doctype_name = "Opening of the Unclaimed Salary Subledger"
    sqlserver_name = "SNOSMREINTEGRONR"
    module_name = "Cuba"

    field_mapping = [
        ("employee",
         ("s2.CPTrabNombre + ' ' + s2.CPTrabPriApellido + ' ' + "
          "s2.CPTrabSegApellido",
          "string")),
        ("amount", ("s.SMrnrImporte", "float")),
        ("reimbursement_date", ("s.SMrnrFecha", "date"))
    ]

    base_query_from = """
        FROM SNOSMREINTEGRONR s join SCPTRABAJADORES s2 on 
        s.CPTrabConsecutivoID = s2.CPTrabConsecutivoID 
        WHERE (s.SMrnrDebito = 0 AND s.SMrnrIdenPaga IS NULL) AND 
        s2.TrabDesactivado = ''
    """

    order_clause = "ORDER BY s.SMrnrIdentificador"

    return export_table_to_json_paginated(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        base_query_from=base_query_from,
        order_clause=order_clause
    )


def get_corte_sc408(db, current_year=None):
    doctype_name = "sc408 model"
    sqlserver_name = "SNOMODSC408CORTE"
    module_name = "Cuba"

    # Si no se proporciona el año actual, lo obtenemos
    if current_year is None:
        current_year = datetime.datetime.now().year

    previous_year = current_year - 1

    # Definimos el mapping con funciones agregadas donde corresponde
    field_mapping = [
        ("employee", ("s2.CPTrabConsecutivoID", 'string')),
        ("employee_name", (
            "MAX(s2.CPTrabNombre + ' ' + s2.CPTrabPriApellido + ' ' + "
            "s2.CPTrabSegApellido)",
            'string')),
        ("year_to_date", ("MAX(s.sccorteanoCalendario)", 'integer')),
        ("month_to_date", ("MAX(s.sccorteMesCalendario)", 'integer')),
        ("worked_days", ("SUM(s.sccorteSalarioTiempoDias)", 'float')),
        ("formed_salary", ("SUM(s.sccorteSalarioTiempoImporte)", 'float')),
        ("total_vacations_accrued", ("SUM(s.sccorteVacacionesDias)", 'float')),
        ("amount_for_accrued_vacations",
         ("SUM(s.sccorteVacacionesImporte)", 'float')),
        ("total_of_subsidies_days", ("SUM(s.sccorteSubsidioDias)", 'float')),
        ("total_amount_of_subsidies",
         ("SUM(s.sccorteSubsidioImporte)", 'float'))
    ]

    # Consulta para contar el total de registros (número de empleados distintos)
    count_query = f"""
        SELECT COUNT(DISTINCT s2.CPTrabConsecutivoID)
        FROM SNOMODSC408CORTE s
        JOIN SCPTRABAJADORES s2 ON s.CPTrabConsecutivoID = 
        s2.CPTrabConsecutivoID
        WHERE (s2.TrabDesactivado = '' OR s2.TrabDesactivado IS NULL)
          AND s.sccorteanoCalendario IN ({current_year}, {previous_year})
    """

    # Consulta base con GROUP BY para obtener los datos agregados
    base_query_from = f"""
        FROM SNOMODSC408CORTE s
        JOIN SCPTRABAJADORES s2 ON s.CPTrabConsecutivoID = 
        s2.CPTrabConsecutivoID
        WHERE (s2.TrabDesactivado = '' OR s2.TrabDesactivado IS NULL)
          AND s.sccorteanoCalendario IN ({current_year}, {previous_year})
        GROUP BY s2.CPTrabConsecutivoID
    """

    order_clause = "ORDER BY s2.CPTrabConsecutivoID"

    # Obtenemos el total de registros primero
    with db.cursor() as cursor:
        cursor.execute(count_query)
        total_items = cursor.fetchone()[0]

    if total_items == 0:
        logging.warning(
            f"No hay datos de Corte para los años {current_year} o "
            f"{previous_year}")
        return []

    # Construimos la consulta SELECT completa con alias y funciones agregadas
    select_clauses = [f"{sql_field} AS {alias}" for alias, (sql_field, _) in
                      field_mapping]
    select_query = (f"SELECT {', '.join(select_clauses)} {base_query_from} "
                    f"{order_clause}")

    return export_table_to_json_paginated(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        base_query_from=base_query_from,
        order_clause=order_clause
    )
