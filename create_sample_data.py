import os
from app import db, Product, Location, ProductMovement
from datetime import datetime, timedelta
import uuid

def add_product(pid, name, sku, desc):
    p = Product(product_id=pid, name=name, sku=sku, description=desc)
    db.session.add(p)

def add_location(lid, name, address):
    l = Location(location_id=lid, name=name, address=address)
    db.session.add(l)

with __name__ == '__main__' or True:
    # create all tables
    db.create_all()

    # clear
    Product.query.delete()
    Location.query.delete()
    ProductMovement.query.delete()

    # realistic sample products
    add_product('P-LAPTOP-001', 'Lenovo ThinkPad X1 Carbon Gen 11', 'LTP-X1C-11', '14" Ultrabook, 16GB RAM, 1TB SSD, Intel i7')
    add_product('P-LAPTOP-002', 'Dell XPS 13 Plus', 'LTP-XPS13P', '13.4" Laptop, 16GB RAM, 512GB SSD, Intel i7')
    add_product('P-MON-001', 'Dell UltraSharp U2723QE 27" 4K Monitor', 'MON-U2723QE', '27" 4K IPS monitor with USB-C')
    add_product('P-KBD-001', 'Logitech MX Keys', 'KBD-MXKEYS', 'Wireless mechanical-like keyboard')
    add_product('P-MOUSE-001', 'Logitech MX Master 3', 'MSE-MX3', 'Advanced ergonomic wireless mouse')
    add_product('P-PRNT-001', 'HP Color LaserJet Pro M255dw', 'PRT-M255', 'Color laser printer, duplex, wireless')
    add_product('P-PHONE-001', 'Apple iPhone 15 Pro', 'PHN-IP15P', 'Smartphone, 256GB, Space Black')
    add_product('P-HEAD-001', 'Sony WH-1000XM5', 'AUD-WH1000XM5', 'Noise cancelling wireless headphones')

    # realistic locations
    add_location('L-MAIN', 'Main Warehouse', '123 Industrial Park, Sector 5')
    add_location('L-SPARE', 'Spare Parts Storage', 'Annex Building, Level 1')
    add_location('L-STORE', 'Retail Storefront', 'Downtown Mall, Shop 12')
    add_location('L-RETURN', 'Returns & QC', 'Quality Control Bay, Dock 3')

    db.session.commit()

    # create movements (inbound deliveries to Main, transfers, store allocations, returns)
    now = datetime.utcnow()
    moves = [
        # inbound shipments to main
        ('P-LAPTOP-001', None, 'L-MAIN', 10),
        ('P-LAPTOP-002', None, 'L-MAIN', 8),
        ('P-MON-001', None, 'L-MAIN', 15),
        ('P-KBD-001', None, 'L-MAIN', 25),
        ('P-MOUSE-001', None, 'L-MAIN', 30),
        ('P-PRNT-001', None, 'L-MAIN', 5),
        ('P-PHONE-001', None, 'L-MAIN', 20),
        ('P-HEAD-001', None, 'L-MAIN', 12),
        # transfer some to spare and store
        ('P-KBD-001', 'L-MAIN', 'L-SPARE', 10),
        ('P-MOUSE-001', 'L-MAIN', 'L-SPARE', 10),
        ('P-LAPTOP-001', 'L-MAIN', 'L-STORE', 3),
        ('P-PHONE-001', 'L-MAIN', 'L-STORE', 5),
        ('P-MON-001', 'L-MAIN', 'L-STORE', 2),
        # returns
        ('P-PHONE-001', 'L-STORE', 'L-RETURN', 1),
        ('P-LAPTOP-002', 'L-MAIN', 'L-RETURN', 1),
        # outbound sales from store
        ('P-LAPTOP-001', 'L-STORE', None, 1),
        ('P-PHONE-001', 'L-STORE', None, 2),
    ]

    for i, (pid, fr, to, q) in enumerate(moves):
        m = ProductMovement(movement_id=str(uuid.uuid4()), timestamp=now - timedelta(days=len(moves)-i), from_location=fr, to_location=to, product_id=pid, qty=q)
        db.session.add(m)

    db.session.commit()
    print('Sample data added.')
