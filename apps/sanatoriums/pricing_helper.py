""" 
Fiyat hesaplama işlemlerini takip etmek ve detaylarını kaydetmek için yardımcı fonksiyonlar
"""

def get_price_details(sanatorium, room_type, price, is_current_season=False, season=None, min_price=None, occupancy=None, children_ages=None):
    """
    Oda fiyatlandırması ile ilgili detaylı bilgileri hazırlar
    
    Args:
        sanatorium: Sanatorium nesnesi
        room_type: RoomType nesnesi
        price: RoomPrice nesnesi
        is_current_season: Mevcut sezon mu
        season: Fiyatın ait olduğu sezon
        min_price: Hesaplanan minimum fiyat (ek yatak fiyatları dahil toplam fiyat)
        occupancy: İstek parametresi olarak gelen kişi sayısı
        children_ages: İstek parametresi olarak gelen çocuk yaşları
        
    Returns:
        dict: Fiyatlandırma detaylarını içeren sözlük
    """
    # İndirim hesaplaması için temel fiyat
    from decimal import Decimal
    base_price = price.price if price else 0
    room_discount_amount = 0
    room_discounted_price = base_price
    
    # Oda fiyatı için indirim hesapla
    if price and hasattr(price, 'discount_type') and hasattr(price, 'discount_value') and price.discount_value:
        if price.discount_type == 'percentage':
            if price.discount_value <= 100:  # Valid percentage
                # Convert float to Decimal for calculation
                discount_percentage = Decimal(str(price.discount_value))
                room_discount_amount = (base_price * discount_percentage) / Decimal('100')
        else:  # fixed amount
            # Convert float to Decimal for calculation
            room_discount_amount = Decimal(str(price.discount_value))
        
        room_discounted_price = max(Decimal('0'), base_price - room_discount_amount)
    
    # min_price için indirim hesaplaması
    min_price_decimal = Decimal(str(min_price)) if min_price is not None else Decimal('0')
    discount_amount = 0
    discounted_price = min_price_decimal
    
    # Eğer fiyat için indirim varsa, aynı indirim yüzdesini min_price'a uygula
    if price and hasattr(price, 'discount_type') and hasattr(price, 'discount_value') and price.discount_value:
        if price.discount_type == 'percentage':
            if price.discount_value <= 100:  # Valid percentage
                discount_percentage = Decimal(str(price.discount_value))
                discount_amount = (min_price_decimal * discount_percentage) / Decimal('100')
        else:  # fixed amount
            # Sabit miktar indirimini direkt olarak kullan
            discount_amount = Decimal(str(price.discount_value))
        
        discounted_price = max(Decimal('0'), min_price_decimal - discount_amount)
    
    details = {
        "sanatorium": {
            "id": sanatorium.id,
            "name": sanatorium.name,
            "location": f"{sanatorium.location.region}, {sanatorium.location.country}" if sanatorium.location else None
        },
        "room": {
            "id": room_type.id,
            "name": room_type.name,
            "min_capacity": room_type.min_capacity,
            "max_capacity": room_type.max_capacity,
            "max_extra_beds": room_type.max_extra_beds,
            "size": room_type.size,
        },
        "pricing": {
            "base_price": base_price,
            "final_price": min_price_decimal,  # Ek yatak fiyatları dahil toplam taban fiyat
            "currency": price.currency.code if price and price.currency else None,
            "with_treatment": price.with_treatment if hasattr(price, 'with_treatment') else None,
            "treatment_option": price.treatment_option.name if hasattr(price, 'treatment_option') and price.treatment_option else None,
            "occupancy": price.occupancy if hasattr(price, 'occupancy') else None,
            "discount": {
                "type": price.discount_type if price and hasattr(price, 'discount_type') else None,
                "value": price.discount_value if price and hasattr(price, 'discount_value') else 0,
                "amount": discount_amount,
                "discounted_price": discounted_price,
                "room_discount_amount": room_discount_amount,
                "room_discounted_price": room_discounted_price
            }
        },
        "season": {
            "name": season.name if season else None,
            "is_current": is_current_season,
            "start_date": season.start_date.strftime('%d.%m.%Y') if season and hasattr(season, 'start_date') else None,
            "end_date": season.end_date.strftime('%d.%m.%Y') if season and hasattr(season, 'end_date') else None,
        },
        "search_criteria": {
            "occupancy": occupancy,
            "children_ages": children_ages,
            "total_guests": (occupancy or 0) + len(children_ages) if children_ages else occupancy,
        }
    }
    
    return details


def get_extra_bed_price_details(room_type, child_age, extra_bed_price, price_added=0, is_default=False):
    """
    Çocuk için ek yatak fiyatı detaylarını hazırlar
    
    Args:
        room_type: Oda tipi
        child_age: Çocuk yaşı
        extra_bed_price: ExtraBedPrice nesnesi
        price_added: Eklenen fiyat
        is_default: Varsayılan fiyat mı yoksa yaş grubuna uygun fiyat mı
        
    Returns:
        dict: Ek yatak fiyatı detaylarını içeren sözlük
    """
    age_group = extra_bed_price.age_group if extra_bed_price else None
    
    # Discount calculations for extra bed price
    from decimal import Decimal
    base_price = extra_bed_price.price if extra_bed_price else 0
    discount_amount = 0
    discounted_price = base_price
    
    if extra_bed_price and hasattr(extra_bed_price, 'discount_type') and hasattr(extra_bed_price, 'discount_value') and extra_bed_price.discount_value:
        if extra_bed_price.discount_type == 'percentage':
            if extra_bed_price.discount_value <= 100:  # Valid percentage
                # Convert float to Decimal for calculation
                discount_percentage = Decimal(str(extra_bed_price.discount_value))
                discount_amount = (base_price * discount_percentage) / Decimal('100')
        else:  # fixed amount
            # Convert float to Decimal for calculation
            discount_amount = Decimal(str(extra_bed_price.discount_value))
        
        discounted_price = max(Decimal('0'), base_price - discount_amount)
    
    details = {
        "child_age": child_age,
        "price_added": price_added,
        "is_default_price": is_default,
        "age_group": {
            "id": age_group.id if age_group else None,
            "name": age_group.name if age_group else None,
            "min_age": age_group.min_age if age_group else None,
            "max_age": age_group.max_age if age_group else None,
        },
        "pricing": {
            "price": base_price,
            "currency": extra_bed_price.currency.code if extra_bed_price and hasattr(extra_bed_price, 'currency') and extra_bed_price.currency else None,
            "with_treatment": extra_bed_price.with_treatment if extra_bed_price and hasattr(extra_bed_price, 'with_treatment') else None,
            "season": extra_bed_price.season.name if extra_bed_price and hasattr(extra_bed_price, 'season') and extra_bed_price.season else None,
            "is_standard": extra_bed_price.is_standard if extra_bed_price and hasattr(extra_bed_price, 'is_standard') else None,
            "discount": {
                "type": extra_bed_price.discount_type if extra_bed_price and hasattr(extra_bed_price, 'discount_type') else None,
                "value": extra_bed_price.discount_value if extra_bed_price and hasattr(extra_bed_price, 'discount_value') else 0,
                "amount": discount_amount,
                "discounted_price": discounted_price
            }
        }
    }
    
    return details
