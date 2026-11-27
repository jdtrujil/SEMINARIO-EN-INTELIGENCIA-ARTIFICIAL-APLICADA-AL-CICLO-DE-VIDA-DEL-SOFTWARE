"""Acceso a la base de datos de las órdenes: PostgreSQL o un archivo SQLite.

Con DATABASE_URL=postgresql://... se usa PostgreSQL 16 (ADR-001), que necesita
el paquete psycopg de requirements.txt. Sin esa variable se usa un archivo
SQLite de la biblioteca estándar, para que el sistema funcione en un equipo
sin PostgreSQL. Las consultas son las mismas en los dos; solo cambian los
tipos de las tablas y el marcador de parámetros.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Iterator, List, Optional, Sequence

from app.cobros.calculo import ItemCobro, ResumenCobro
from app.ordenes.modelos import (
    ETAPAS,
    HORA_COLOMBIA,
    RECIBIDA,
    TERMINADA,
    CambioDeEtapa,
    Mecanico,
    OrdenTaller,
)

_TABLAS_SQLITE = (
    """CREATE TABLE IF NOT EXISTS mecanicos (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS ordenes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero TEXT NOT NULL UNIQUE,
        placa TEXT NOT NULL,
        observaciones TEXT NOT NULL,
        mecanico_id INTEGER NOT NULL REFERENCES mecanicos(id),
        etapa TEXT NOT NULL,
        fecha_ingreso TEXT NOT NULL,
        total_repuestos INTEGER,
        total_mano_obra INTEGER,
        total INTEGER)""",
    """CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        orden_id INTEGER NOT NULL REFERENCES ordenes(id),
        tipo TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        precio_unitario INTEGER NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS historial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        orden_id INTEGER NOT NULL REFERENCES ordenes(id),
        etapa TEXT NOT NULL,
        fecha_hora TEXT NOT NULL)""",
)

_TABLAS_POSTGRES = (
    """CREATE TABLE IF NOT EXISTS mecanicos (
        id SMALLINT PRIMARY KEY,
        nombre TEXT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS ordenes (
        id BIGSERIAL PRIMARY KEY,
        numero CHAR(8) NOT NULL UNIQUE,
        placa VARCHAR(6) NOT NULL,
        observaciones TEXT NOT NULL,
        mecanico_id SMALLINT NOT NULL REFERENCES mecanicos(id),
        etapa VARCHAR(20) NOT NULL
            CHECK (etapa IN ('Recibida', 'En reparación', 'Terminada')),
        fecha_ingreso TIMESTAMPTZ NOT NULL,
        total_repuestos BIGINT,
        total_mano_obra BIGINT,
        total BIGINT)""",
    """CREATE TABLE IF NOT EXISTS items (
        id BIGSERIAL PRIMARY KEY,
        orden_id BIGINT NOT NULL REFERENCES ordenes(id),
        tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('repuesto', 'mano de obra')),
        descripcion TEXT NOT NULL,
        cantidad INTEGER NOT NULL CHECK (cantidad >= 1),
        precio_unitario BIGINT NOT NULL CHECK (precio_unitario >= 0))""",
    """CREATE TABLE IF NOT EXISTS historial (
        id BIGSERIAL PRIMARY KEY,
        orden_id BIGINT NOT NULL REFERENCES ordenes(id),
        etapa VARCHAR(20) NOT NULL,
        fecha_hora TIMESTAMPTZ NOT NULL)""",
)

_INDICES = (
    "CREATE INDEX IF NOT EXISTS ordenes_placa ON ordenes (placa)",
    "CREATE INDEX IF NOT EXISTS items_orden ON items (orden_id)",
    "CREATE INDEX IF NOT EXISTS historial_orden ON historial (orden_id)",
)

_DROP = {
    "historial": "DROP TABLE IF EXISTS historial",
    "items": "DROP TABLE IF EXISTS items",
    "ordenes": "DROP TABLE IF EXISTS ordenes",
    "mecanicos": "DROP TABLE IF EXISTS mecanicos",
}

_SELECT_ORDEN = (
    "SELECT id, numero, placa, observaciones, mecanico_id, etapa, fecha_ingreso, "
    "total_repuestos, total_mano_obra, total FROM ordenes WHERE numero = ?"
)
_SELECT_RECIENTES = (
    "SELECT id, numero, placa, observaciones, mecanico_id, etapa, fecha_ingreso, "
    "total_repuestos, total_mano_obra, total FROM ordenes "
    "ORDER BY fecha_ingreso DESC, id DESC LIMIT ?"
)


def es_postgres(destino: str) -> bool:
    """Indica si el destino es una URL de PostgreSQL."""
    return destino.startswith(("postgresql://", "postgres://"))


@contextmanager
def abrir(destino: str) -> Iterator["Repositorio"]:
    """Abre la base de datos y confirma los cambios al salir sin errores.

    Parámetros:
        destino: una URL postgresql://... o la ruta de un archivo SQLite.

    Si algo falla dentro del bloque, deshace los cambios de ese bloque.
    """
    if es_postgres(destino):
        import psycopg  # solo hace falta con PostgreSQL

        conexion: Any = psycopg.connect(destino)
        dialecto = "postgres"
    else:
        conexion = sqlite3.connect(destino)
        conexion.execute("PRAGMA foreign_keys = ON")
        dialecto = "sqlite"
    try:
        yield Repositorio(conexion, dialecto)
        conexion.commit()
    except BaseException:
        conexion.rollback()
        raise
    finally:
        conexion.close()


class Repositorio:
    """Guarda y lee las órdenes con una conexión ya abierta."""

    def __init__(self, conexion: Any, dialecto: str) -> None:
        self._conexion = conexion
        self._dialecto = dialecto

    # --- Utilidades internas ---------------------------------------------

    def _ejecutar(self, sql: str, parametros: Sequence[object] = ()) -> Any:
        if self._dialecto == "postgres":
            sql = sql.replace("?", "%s")
        cursor = self._conexion.cursor()
        cursor.execute(sql, tuple(parametros))
        return cursor

    def _fecha_a_bd(self, fecha: datetime) -> object:
        return fecha if self._dialecto == "postgres" else fecha.isoformat()

    @staticmethod
    def _fecha_de_bd(valor: object) -> datetime:
        fecha = (
            valor if isinstance(valor, datetime) else datetime.fromisoformat(str(valor))
        )
        return fecha.astimezone(HORA_COLOMBIA)

    def _id_orden(self, numero: str) -> Optional[int]:
        fila = self._ejecutar(
            "SELECT id FROM ordenes WHERE numero = ?", (numero,)
        ).fetchone()
        return None if fila is None else int(fila[0])

    # --- Esquema y mecánicos ---------------------------------------------

    def crear_tablas(self) -> None:
        """Crea las tablas y los índices si no existen."""
        tablas = _TABLAS_POSTGRES if self._dialecto == "postgres" else _TABLAS_SQLITE
        for sql in tablas + _INDICES:
            self._ejecutar(sql)

    def guardar_mecanicos(self, mecanicos: Sequence[Mecanico]) -> None:
        """Crea o actualiza los mecánicos con los nombres configurados."""
        for mecanico in mecanicos:
            self._ejecutar(
                "INSERT INTO mecanicos (id, nombre) VALUES (?, ?) "
                "ON CONFLICT (id) DO UPDATE SET nombre = excluded.nombre",
                (mecanico.id, mecanico.nombre),
            )

    def mecanicos(self) -> List[Mecanico]:
        filas = self._ejecutar(
            "SELECT id, nombre FROM mecanicos ORDER BY id"
        ).fetchall()
        return [Mecanico(int(i), str(n)) for i, n in filas]

    # --- Órdenes ---------------------------------------------------------

    def existe_numero(self, numero: str) -> bool:
        return self._id_orden(numero) is not None

    def orden_abierta_de_placa(self, placa: str) -> Optional[str]:
        """Número de la orden no terminada de esa placa, si hay una."""
        fila = self._ejecutar(
            "SELECT numero FROM ordenes WHERE placa = ? AND etapa <> ?",
            (placa, TERMINADA),
        ).fetchone()
        return None if fila is None else str(fila[0]).strip()

    def crear_orden(
        self,
        numero: str,
        placa: str,
        observaciones: str,
        mecanico_id: int,
        fecha: datetime,
    ) -> None:
        """Guarda el ingreso en la etapa Recibida y su primera línea de historial."""
        self._ejecutar(
            "INSERT INTO ordenes (numero, placa, observaciones, mecanico_id, etapa, "
            "fecha_ingreso) VALUES (?, ?, ?, ?, ?, ?)",
            (
                numero,
                placa,
                observaciones,
                mecanico_id,
                RECIBIDA,
                self._fecha_a_bd(fecha),
            ),
        )
        self._agregar_historial(numero, RECIBIDA, fecha)

    def _agregar_historial(self, numero: str, etapa: str, fecha: datetime) -> None:
        self._ejecutar(
            "INSERT INTO historial (orden_id, etapa, fecha_hora) VALUES (?, ?, ?)",
            (self._id_orden(numero), etapa, self._fecha_a_bd(fecha)),
        )

    def orden(self, numero: str) -> Optional[OrdenTaller]:
        """La orden completa, con sus ítems e historial, o None si no existe."""
        fila = self._ejecutar(_SELECT_ORDEN, (numero,)).fetchone()
        return None if fila is None else self._orden_desde_fila(fila)

    def ordenes_recientes(self, limite: int = 50) -> List[OrdenTaller]:
        """Las órdenes más recientes primero, para la lista del taller."""
        filas = self._ejecutar(
            _SELECT_RECIENTES,
            (limite,),
        ).fetchall()
        return [self._orden_desde_fila(fila) for fila in filas]

    def _orden_desde_fila(self, fila: Sequence[Any]) -> OrdenTaller:
        orden_id = fila[0]
        items = [
            ItemCobro(str(t), str(d), int(c), int(p))
            for t, d, c, p in self._ejecutar(
                "SELECT tipo, descripcion, cantidad, precio_unitario FROM items "
                "WHERE orden_id = ? ORDER BY id",
                (orden_id,),
            ).fetchall()
        ]
        historial = [
            CambioDeEtapa(str(e), self._fecha_de_bd(f))
            for e, f in self._ejecutar(
                "SELECT etapa, fecha_hora FROM historial "
                "WHERE orden_id = ? ORDER BY id",
                (orden_id,),
            ).fetchall()
        ]
        factura = None
        if fila[9] is not None:
            factura = ResumenCobro(int(fila[7]), int(fila[8]), int(fila[9]))
        etapa = str(fila[5])
        if etapa not in ETAPAS:
            raise ValueError(f"Etapa desconocida en la base de datos: {etapa}")
        return OrdenTaller(
            numero=str(fila[1]).strip(),
            placa=str(fila[2]),
            observaciones=str(fila[3]),
            mecanico_id=int(fila[4]),
            etapa=etapa,
            fecha_ingreso=self._fecha_de_bd(fila[6]),
            items=items,
            historial=historial,
            factura=factura,
        )

    def agregar_item(self, numero: str, item: ItemCobro) -> None:
        """Guarda un repuesto o una mano de obra ya validados."""
        self._ejecutar(
            "INSERT INTO items "
            "(orden_id, tipo, descripcion, cantidad, precio_unitario) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                self._id_orden(numero),
                item.tipo,
                item.descripcion,
                item.cantidad,
                item.precio_unitario,
            ),
        )

    def cambiar_etapa(
        self,
        numero: str,
        etapa: str,
        fecha: datetime,
        factura: Optional[ResumenCobro] = None,
    ) -> None:
        """Cambia la etapa, guarda la factura si hay y agrega la línea del historial."""
        if factura is None:
            self._ejecutar(
                "UPDATE ordenes SET etapa = ? WHERE numero = ?", (etapa, numero)
            )
        else:
            self._ejecutar(
                "UPDATE ordenes SET etapa = ?, total_repuestos = ?, "
                "total_mano_obra = ?, total = ? WHERE numero = ?",
                (
                    etapa,
                    factura.total_repuestos,
                    factura.total_mano_obra,
                    factura.total,
                    numero,
                ),
            )
        self._agregar_historial(numero, etapa, fecha)

    def eliminar_tablas(self) -> None:
        """Borra todas las tablas. Solo lo usan las pruebas con PostgreSQL."""
        for tabla in ("historial", "items", "ordenes", "mecanicos"):
            self._ejecutar(_DROP[tabla])

    def comprobar(self) -> None:
        """Hace una consulta mínima; lanza un error si la base no responde."""
        self._ejecutar("SELECT 1").fetchone()
