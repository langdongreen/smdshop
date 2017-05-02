import math

product_list = {-2: ('Ordering Service','',0,0),
                -1: ('Assembly', '', 0, 4.00),
                1: ('QFN16-0.5mm','DIP', 16,0.34),
                2: ('QFN16-0.65mm','DIP', 16,0.34),
                3: ('QFN20-0.5mm','DIP', 20,0.45),
                4: ('QFN20-0.65mm','DIP', 20,0.45),
                5: ('QFP44-0.8mm','DIP', 44,0.78),
                6: ('QFP32-0.8mm','DIP', 32,0.67),
                7: ('QFP64-0.5mm','DIP', 64,0.78),
                8: ('QFN64-0.5mm','DIP', 64,0.78),
                9: ('TSSOP14-0.65mm','DIP', 14,0.34),
                10: ('SOP24-1mm','DIP', 24,0.45),
                11: ('SOP32-1.27mm','DIP', 32,0.78),
                12: ('SP34','DIP', 8,0.34),
                13: ('SO14-1.27mm','DIP',14,0.34) }

#assembly = base_rate + math.ceil(pins * perpin)
#calculate and add to product_list
base_rate = 4
per_pin = 0.15

for p in product_list:
    a = math.ceil(product_list[p][2] * per_pin) + base_rate
    product_list[p] = product_list[p] + (a,)

shipping = 8.25
ordering_service = 1.3
