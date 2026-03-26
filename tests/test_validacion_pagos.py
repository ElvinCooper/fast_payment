import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from app.utils.pagos import validar_monto_pago


def test_validar_monto_pago_exito():
    """Test cuando el monto es menor o igual a la deuda total"""
    cursor = MagicMock()

    # Mockear el resultado del query
    cursor.fetchone.return_value = (
        10000.0,
        5000.0,
        500.0,
    )  # vprestamo, deuda_al_dia, mora_total

    resultado = validar_monto_pago(cursor, 123, 1, 5000.0)

    assert resultado["vprestamo"] == 10000.0
    assert resultado["deuda_al_dia"] == 5000.0
    assert resultado["mora_total"] == 500.0
    assert resultado["total_deuda"] == 5500.0
    assert resultado["puede_pagar"]
    assert resultado["diferencia"] == -500.0  # 5000 - 5500

    # Verificar que se ejecutó el query con los parámetros correctos
    cursor.execute.assert_called_once()


def test_validar_monto_pago_excede_deuda():
    """Test cuando el monto excede la deuda total"""
    cursor = MagicMock()

    # Mockear el resultado del query
    cursor.fetchone.return_value = (
        10000.0,
        5000.0,
        500.0,
    )  # vprestamo, deuda_al_dia, mora_total

    resultado = validar_monto_pago(cursor, 123, 1, 6000.0)

    assert resultado["vprestamo"] == 10000.0
    assert resultado["deuda_al_dia"] == 5000.0
    assert resultado["mora_total"] == 500.0
    assert resultado["total_deuda"] == 5500.0
    assert not resultado["puede_pagar"]
    assert resultado["diferencia"] == 500.0  # 6000 - 5500


def test_validar_monto_pago_sin_deuda():
    """Test cuando no hay deuda ni mora"""
    cursor = MagicMock()

    # Mockear el resultado con valores nulos
    cursor.fetchone.return_value = (
        10000.0,
        0.0,
        0.0,
    )  # vprestamo, deuda_al_dia, mora_total

    resultado = validar_monto_pago(cursor, 123, 1, 0.0)

    assert resultado["vprestamo"] == 10000.0
    assert resultado["deuda_al_dia"] == 0.0
    assert resultado["mora_total"] == 0.0
    assert resultado["total_deuda"] == 0.0
    assert resultado["puede_pagar"]
    assert resultado["diferencia"] == 0.0


def test_validar_monto_pago_prestamo_no_existe():
    """Test cuando el préstamo no existe"""
    cursor = MagicMock()

    # Mockear que no hay resultados
    cursor.fetchone.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        validar_monto_pago(cursor, 123, 999, 1000.0)

    assert exc_info.value.status_code == 404
    assert "Préstamo no encontrado o ya está pagado" in str(exc_info.value.detail)
