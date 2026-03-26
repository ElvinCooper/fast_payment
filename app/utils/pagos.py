from fastapi import HTTPException


def validar_monto_pago(
    cursor, id_cliente: int, n_prestamo: int, monto_pago: float
) -> dict:
    """
    Valida si el monto del pago no excede el saldo pendiente total
    (deuda actual + mora acumulada)

    Args:
        cursor: Cursor de base de datos activo
        id_cliente: ID del cliente
        n_prestamo: Número del préstamo
        monto_pago: Monto del pago a validar (puede ser Decimal o float)

    Returns:
        dict: {
            'vprestamo': float,  # Monto original del préstamo
            'deuda_al_dia': float,  # Deuda actual de cuotas vencidas
            'mora_total': float,  # Intereses de mora acumulados
            'total_deuda': float,  # Total deuda (deuda_al_dia + mora_total)
            'puede_pagar': bool,  # Si el monto es válido
            'diferencia': float  # Diferencia entre monto_pago y total_deuda
        }

    Raises:
        HTTPException: Si el préstamo no existe
    """

    # Query basado en el de clientes.py para obtener deuda y mora
    query = """
        SELECT
            PR.vprestamo,
            IFNULL(CV.deuda_al_dia, 0) AS deuda_al_dia,
            IFNULL(MORA.mora_total, 0) AS mora_total
        FROM prestamo PR
        LEFT JOIN (
            SELECT
                G.nprestamo,
                SUM(IFNULL(G.vpendiente, 0)) AS deuda_al_dia
            FROM pagos G
            WHERE G.fechaven <= SYSDATE()
            AND G.estatus = 0
            GROUP BY G.nprestamo
        ) CV ON PR.nprestamo = CV.nprestamo
        LEFT JOIN (
            SELECT
                nprestamo,
                SUM(ROUND(mora_calc, 2)) AS mora_total
            FROM (
                SELECT
                    pa.nprestamo,
                    CASE
                        WHEN p.fpago IN (1, 4, 5) THEN
                            (pa.vpendiente * p.mora / 100.0 / 30.0) * DATEDIFF(SYSDATE(), pa.fechaplazo)
                        WHEN p.fpago IN (2, 7) THEN
                            (pa.vpendiente * p.mora / 100.0 / 4.0 / 7.0) * DATEDIFF(SYSDATE(), pa.fechaplazo)
                        WHEN p.fpago IN (3, 6) THEN
                            (pa.vpendiente * p.mora / 100.0 / 2.0 / 15.0) * DATEDIFF(SYSDATE(), pa.fechaplazo)
                    END AS mora_calc
                FROM pagos pa
                JOIN prestamo p ON pa.nprestamo = p.nprestamo
                WHERE pa.fechaplazo <= SYSDATE()
                    AND pa.vpendiente > 0
                    AND DATEDIFF(SYSDATE(), pa.fechaplazo) > 0
            ) calc_mora
            GROUP BY nprestamo
        ) MORA ON PR.nprestamo = MORA.nprestamo
        WHERE PR.codigo = %s AND PR.nprestamo = %s AND PR.pagado != 1
    """

    cursor.execute(query, (id_cliente, n_prestamo))
    resultado = cursor.fetchone()

    if not resultado:
        raise HTTPException(
            status_code=404, detail="Préstamo no encontrado o ya está pagado"
        )

    vprestamo = float(resultado[0] or 0)
    deuda_al_dia = float(resultado[1] or 0)
    mora_total = float(resultado[2] or 0)
    total_deuda = deuda_al_dia + mora_total

    # Convertir monto_pago a float si es Decimal
    monto_pago_float = float(monto_pago)

    return {
        "vprestamo": vprestamo,
        "deuda_al_dia": deuda_al_dia,
        "mora_total": mora_total,
        "total_deuda": total_deuda,
        "puede_pagar": monto_pago_float <= total_deuda,
        "diferencia": monto_pago_float - total_deuda,
    }
