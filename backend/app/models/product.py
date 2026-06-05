from dataclasses import dataclass


@dataclass
class Product:
    id: int
    name: str
    sku: str
    unit_price: float
    pack_size: int
